from fleetmanager.fleet_simulation.util import fleet_simulator
from fleetmanager.api.fleet_simulation.schemas import FleetSimulationOptions
from fleetmanager.tests.fixtures.fleet_simulation_requests import simulation_request_naive, simulation_request_intelligent


def test_fleet_simulator_naive():
    """
    Tests the utility function used by the fleet-simulation/simulation endpoint
    model module, which invokes most code in model.py and vehicle.py
    """
    options = FleetSimulationOptions(**simulation_request_naive)
    results = fleet_simulator(options)
    assert type(results) is dict, f"The returned type is {type(results)}, expected dict"
    assert results.get("number_of_trips", 0) != 0, "Did not find any dummy trips"
    result_current = len(results["simulation_options"].current_vehicles)
    input_current = len(simulation_request_naive["current_vehicles"])
    input_simulation = sum(
        vehicle.get("simulation_count", 0)
        for vehicle in simulation_request_naive["simulation_vehicles"]
    )
    result_simulation = (
        len(results["results"].get("vehicle_usage", dict()).get("simulation", [])) - 1
    )  # minus one because we add a "Medarbejder bil"
    assert (
        input_current == result_current
    ), f"Current vehicles was not correctly set in simulation, input: {input_current}, simulation: {result_current}"
    assert (
        input_simulation == result_simulation
    ), f"Simulation vehicles was not correctly set in simulation, input: {input_simulation}, simulation: {result_simulation}"
    assert (
        sum(
            day.get("Antal ikke allokeret", 0)
            for day in results.get("results", dict()).get("unallocated_pr_day", [])
        )
        == 0
    ), "Unallocated trips was above 0"
    assert 1 == 1, f"results {results}"


def test_fleet_simulator_intelligent():
    """
    Tests the utility function used by the fleet-simulation/simulation endpoint
    model module, which invokes most code in model.py and vehicle.py
    """
    options = FleetSimulationOptions(**simulation_request_intelligent)
    results = fleet_simulator(options)
    assert type(results) is dict, f"The returned type is {type(results)}, expected dict"
    assert results.get("number_of_trips", 0) != 0, "Did not find any dummy trips"
    result_current = len(results["simulation_options"].current_vehicles)
    input_current = len(simulation_request_intelligent["current_vehicles"])
    input_simulation = sum(
        vehicle.get("simulation_count", 0)
        for vehicle in simulation_request_intelligent["simulation_vehicles"]
    )
    result_simulation = (
        len(results["results"].get("vehicle_usage", dict()).get("simulation", [])) - 1
    )  # minus one because we add a "Medarbejder bil"
    assert (
        input_current == result_current
    ), f"Current vehicles was not correctly set in simulation, input: {input_current}, simulation: {result_current}"
    assert (
        input_simulation == result_simulation
    ), f"Simulation vehicles was not correctly set in simulation, input: {input_simulation}, simulation: {result_simulation}"
    assert (
        sum(
            day.get("Antal ikke allokeret", 0)
            for day in results.get("results", dict()).get("unallocated_pr_day", [])
        )
        == 0
    ), "Unallocated trips was above 0"
    assert 1 == 1, f"results {results}"
