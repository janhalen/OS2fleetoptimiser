import numpy as np

from fleetmanager.api.goal_simulation.schemas import GoalSimulationOptions
from fleetmanager.goal_simulation.util import goal_simulator
from fleetmanager.tests.fixtures.goal_simulation_request import simulation_request


def test_goal_simulation_remove():
    """ """
    options = GoalSimulationOptions(**simulation_request)
    results = goal_simulator(options)
    key_types = [
        ("current_expense", [int]),
        ("simulation_expense", [int]),
        ("current_co2e", [float, np.float64]),
        ("simulation_co2e", [float, np.float64]),
        ("unallocated", [int]),
        ("vehicles", [list]),
    ]
    assert type(results) is dict, f"The returned type is {type(results)}, expected dict"
    assert results.get("number_of_trips", 0) != 0, "Did not find any dummy trips"
    result_current = len(results["simulation_options"].current_vehicles)
    input_current = len(simulation_request["current_vehicles"])

    assert (
        input_current == result_current
    ), f"Current vehicles was not correctly set in goal simulation, input: {input_current}, simulation: {result_current}"

    assert (
        len(results.get("solutions", [])) != 0
    ), "No solutions were returned by utility tabu function"
    assert all(
        [
            type(getattr(results.get("solutions")[0], key)) in value_type
            for key, value_type in key_types
        ]
    ), f"Solution results are not in expected " \
       f"type {[type(getattr(results.get('solutions')[0], key)) for key, value_type in key_types]}"


def test_goal_simulation_add():
    """ """
    simulation_request_cleaned = simulation_request.copy()
    simulation_request_cleaned["fixed_vehicles"] = []
    options = GoalSimulationOptions(**simulation_request_cleaned)
    results = goal_simulator(options)
    key_types = [
        ("current_expense", [int]),
        ("simulation_expense", [int]),
        ("current_co2e", [float, np.float64]),
        ("simulation_co2e", [float, np.float64]),
        ("unallocated", [int]),
        ("vehicles", [list]),
    ]
    assert type(results) is dict, f"The returned type is {type(results)}, expected dict"
    assert results.get("number_of_trips", 0) != 0, "Did not find any dummy trips"
    result_current = len(results["simulation_options"].current_vehicles)
    input_current = len(simulation_request_cleaned["current_vehicles"])

    assert (
        input_current == result_current
    ), f"Current vehicles was not correctly set in goal simulation, input: {input_current}, simulation: {result_current}"

    assert (
        len(results.get("solutions", [])) != 0
    ), "No solutions were returned by utility tabu function"
    assert all(
        [
            type(getattr(results.get("solutions")[0], key)) in value_type
            for key, value_type in key_types
        ]
    ), f"Solution results are not in expected " \
       f"type {[type(getattr(results.get('solutions')[0], key)) for key, value_type in key_types]}"
