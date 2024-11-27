from datetime import datetime, timedelta

from fleetmanager.model.roundtripaggregator import (
    split_roundtrip,
    returns_to_home,
    sanitise_for_overlaps,
    get_overlap_mask,
)
from fleetmanager.tests.fixtures.extractor_data import (
    roundtrip,
    frame_trips,
    start_locations,
)


def test_split_roundtrip():
    split_roundtrips = split_roundtrip(
        roundtrip,
        timedelta(minutes=30),
        duration_limit=timedelta(hours=10),
        distance_criteria=0.1,
    )

    assert (
        len(split_roundtrips) == 3
    ), f"Split roundtrips was not the expected length 3, but {len(split_roundtrips)}"
    assert all(
        [
            len(new_roundtrip) == expected_length
            for new_roundtrip, expected_length in zip(split_roundtrips, [2, 1, 1])
        ]
    ), f"The new roundtrips did not split as expected"


def test_returns_to_home():
    it_returns_to_home = returns_to_home(
        trips=frame_trips,
        current_trip_index=0,
        home=3,
        allowed_starts=start_locations,
        search_time=datetime(2023, 1, 1),
        home_criteria=0.1,
    )
    assert it_returns_to_home


def test_sanitation():
    overlapping = frame_trips.copy()
    overlapping.loc[1, "end_time"] = datetime(2022, 4, 1, 2, 41, 0)
    cleaned = sanitise_for_overlaps(overlapping)
    mask = get_overlap_mask(cleaned)
    assert len(mask) == 2, f"Mask of cleaned was not expected length 2, but {len(mask)}"
    assert all(mask), f"Cleaned was not properly sanitised"
    assert len(cleaned) == 3, f"Sanitised did not remove the overlapping log"
