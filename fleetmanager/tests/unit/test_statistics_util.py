from datetime import date, datetime, time, timedelta
from io import BytesIO

import pandas as pd

from fleetmanager.statistics.util import (
    get_summed_statistics,
    carbon_neutral_share,
    emission_series,
    total_driven,
    daily_driving,
    driving_data_to_excel,
)

start_date = date(2022, 3, 1)
end_date = date(2022, 3, 31)
extra_day = timedelta(days=3)


def test_summed_statistics(db_session):
    statistics_overview = get_summed_statistics(db_session)

    assert (
        statistics_overview.total_roundtrips == 2188
    ), f"Number of total roundtrips was unexpected, {statistics_overview.total_roundtrips}"
    assert (
        statistics_overview.first_date == start_date
    ), f"First roundtrip date was unexpected date, {statistics_overview.first_date}"
    assert (
        statistics_overview.last_date == end_date
    ), f"Last roundtrip date was unexpected date, {statistics_overview.last_date}"
    assert (
        statistics_overview.total_driven == 34605
        or statistics_overview.total_driven == 12
    ), f"Total driven was unexpected km, {statistics_overview.total_driven}"
    assert (
        round(statistics_overview.total_emission, 3) == 1.575
        or round(statistics_overview.total_emission, 6) == 0.000181
    ), f"Total emission was unexpected, {statistics_overview.total_emission}"
    assert (
        statistics_overview.share_carbon_neutral == 75
        or statistics_overview.share_carbon_neutral == 100
    ), f"Share of carbon neutral driving was unexpected, {statistics_overview.share_carbon_neutral}"


def test_carbon_neutral_share(db_session):
    carbon_neutral_share_trend = carbon_neutral_share(
        db_session,
        start_date=datetime.combine(start_date, time(0, 0, 0)),
        end_date=datetime.combine(end_date, time(0, 0, 0)) + extra_day,
    )

    assert (
        len(carbon_neutral_share_trend["x"]) == 1
    ), f"There wasn't the expected number of entries, {len(carbon_neutral_share_trend['x'])}"
    assert (
        round(
            sum(carbon_neutral_share_trend["y"]) / len(carbon_neutral_share_trend["y"])
        )
        == 100
    ), f"The carbon neutral share is not the expected 100%"


def test_emission_series(db_session):
    emission_series_trend = emission_series(
        db_session,
        start_date=datetime.combine(start_date, time(0, 0, 0)),
        end_date=datetime.combine(end_date, time(0, 0, 0)) + extra_day,
    )

    assert (
        len(emission_series_trend["x"]) == 1
    ), f"There wasn't the expected number of entries, {len(emission_series_trend['x'])}"
    assert (
        round(sum(emission_series_trend["y"]), 7) == 0.0001807
    ), f"The total emission is not the expected 0.0001807"


def test_total_driven(db_session):
    total_driven_trend = total_driven(
        db_session,
        start_date=datetime.combine(start_date, time(0, 0, 0)),
        end_date=datetime.combine(end_date, time(0, 0, 0)) + extra_day,
    )

    assert (
        len(total_driven_trend["x"]) == 1
    ), f"There wasn't the expected number ofr entries, {len(total_driven_trend['x'])}"
    assert (
        round(sum(total_driven_trend["y"]), 3) == 12.306
    ), f"Total driven doesn't sum to the expected: 12.306"


def test_daily_driving_and_export(db_session):
    response = daily_driving(
        db_session,
        start_date=datetime.combine(start_date, time(0, 0, 0)),
        end_date=datetime.combine(end_date, time(0, 0, 0)) + extra_day,
        include_trip_segments=True,
        locations=[1, 2, 3],
    )

    response_with_additional_filters = daily_driving(
        db_session,
        start_date=datetime.combine(start_date, time(0, 0, 0)),
        end_date=datetime.combine(end_date, time(0, 0, 0)) + extra_day,
        vehicles=[
            202,
            203,
            204,
            206,
            209,
            211,
            220,
            221,
            224,
            235,
            237,
            239,
            240,
            245,
            246,
            247,
            250,
            254,
            257,
            270,
            274,
            275,
            277,
            282,
            322,
            332,
            333,
            352,
            355,
        ],
    )

    assert (
        response["query_start_date"]
        == response_with_additional_filters["query_start_date"]
    )
    assert (
        response["query_end_date"] == response_with_additional_filters["query_end_date"]
    )
    assert (
        response["query_locations"]
        == response_with_additional_filters["query_locations"]
    )
    assert (
        response["query_vehicles"] == response_with_additional_filters["query_vehicles"]
    )
    assert response["shifts"] == response_with_additional_filters["shifts"]
    assert len(response["driving_data"]) > 10
    assert len(response["driving_data"]) == len(
        response_with_additional_filters["driving_data"]
    )

    stream = driving_data_to_excel(response, 40)
    assert (
        type(stream) == BytesIO
    ), f"Returned stream is not expected type BytesIO, but {type(stream)}"
    save_file = "excel_export_activity.xlsx"
    with open(save_file, "wb") as f:
        f.write(stream.read())

    saved_file = pd.read_excel(save_file, index_col=0)
    assert saved_file.iloc[3, 1] == 8
    assert saved_file.iloc[2, 0] == 19.4
    assert saved_file.iloc[34, 22] == 37.1
