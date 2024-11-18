from datetime import date, timedelta

from fleetmanager.configuration.util import move_vehicle
from fleetmanager.simulation_setup.util import get_location_vehicles


def test_get_location_vehicles(db_session):
    start = date(2022, 3, 1)
    end = date(2023, 5, 1)

    # pull the original
    location_vehicles = get_location_vehicles(
        db_session, start_date=start, end_date=end
    )

    # move a vehicle
    move_vehicle(db_session, vehicle_id=277, from_date=date(2022, 3, 15), to_location=1)

    # test the oldlocation
    location_vehicles_moved = get_location_vehicles(
        db_session, start_date=start, end_date=end
    )
    vehicle_expectations = [
        {"id": 1, "count": 6},
        {"id": 2, "count": 17},
        {"id": 3, "count": 6},
    ]
    vehicle_moved_expectations = [
        {"id": 1, "count": 7},
        {"id": 2, "count": 17},
        {"id": 3, "count": 6},
    ]

    assert len(location_vehicles.locations) == len(
        vehicle_expectations
    ), "Expected 3 locations returned"
    assert len(location_vehicles_moved.locations) == len(
        vehicle_expectations
    ), "Expected 3 locations returned"
    assert all(
        map(
            lambda location_expectation: len(
                next(
                    filter(
                        lambda location: location.id == location_expectation["id"],
                        location_vehicles.locations,
                    )
                ).vehicles
            )
            == location_expectation["count"],
            vehicle_expectations,
        )
    ), "Some locations did not hold the expected number of vehicles"

    assert all(
        map(
            lambda location_expectation: len(
                next(
                    filter(
                        lambda location: location.id == location_expectation["id"],
                        location_vehicles_moved.locations,
                    )
                ).vehicles
            )
            == location_expectation["count"],
            vehicle_moved_expectations,
        )
    ), "Some locations did not hold the expected number of vehicles"

    def vehicle_getter(data, vehicle_id, location_id):
        return next(
            filter(
                lambda vehicles: vehicles.id == vehicle_id,
                next(
                    filter(
                        lambda location: location.id == location_id,
                        data,
                    )
                ).vehicles,
            )
        )

    vehicle_location_1_277 = vehicle_getter(location_vehicles_moved.locations, 277, 1)
    vehicle_location_2_277 = vehicle_getter(location_vehicles_moved.locations, 277, 2)
    vehicle_location_2_333 = vehicle_getter(location_vehicles.locations, 333, 2)

    assert (
        vehicle_location_1_277.status == "ok"
    ), 'Vehicle 277 did not have the expected "ok" status at location 1'
    assert (
        vehicle_location_2_277.status == "locationChanged"
    ), 'Vehicle 277 did not have the expeceted "locationChanged" at its old location; 2'
    assert (
        vehicle_location_2_333.status == "leasingEnded"
    ), 'Vehicle 333 did not have the expected "leasingEnded" status'

    not_active = get_location_vehicles(
        db_session, start_date=start + timedelta(weeks=10), end_date=end
    )

    vehicle_location_2_277 = vehicle_getter(not_active.locations, 277, 1)

    assert (
        vehicle_location_2_277.status == "notActive"
    ), 'Vehicle 277 did not have the expected "notActive" status'
