from fleetmanager.model.roundtripaggregator import aggregator
from fleetmanager.tests.fixtures.extractor_data import car, car_trips, start_locations


def test_extractor_aggregation():
    """
    Testing that the major aggregator function works. Dummy data should be aggregated to one roundtrip that is
    the aggregation type complete.
    """
    roundtrips = aggregator(
        car=car,
        car_trips=car_trips,
        allowed_starts=start_locations,
    )

    assert len(roundtrips) >= 1, "Aggregator did not aggregate any roundtrips"
    assert any(
        ["complete" in roundtrip.get("aggregation_type") for roundtrip in roundtrips]
    )
