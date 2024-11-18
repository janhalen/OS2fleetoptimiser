from io import BytesIO

import pandas as pd

from fleetmanager.api.fleet_simulation.schemas import FleetSimulationOptions
from fleetmanager.fleet_simulation.util import simulation_results_to_excel
from fleetmanager.tests.fixtures.fleet_simulation_results import results


def test_excel_fleet_simulation_export(db_session):
    """
    Test function for the excel export feature after running fleet simulation. Saves a file locally and
    tests that the first entry in the first sheet is equal to the input driving book.
    """
    results["result"]["simulation_options"] = FleetSimulationOptions(
        **results["result"]["simulation_options"]
    )
    stream, location = simulation_results_to_excel(
        results.get("result"), db_session
    )
    assert type(location) == str, f"Location is not string, but type {type(location)}"
    assert (
        type(stream) == BytesIO
    ), f"Returned stream is not expected type BytesIO, but {type(stream)}"
    save_file = "excel_export_test.xlsx"
    with open(save_file, "wb") as f:
        f.write(stream.read())

    saved_file = pd.read_excel(save_file)
    assert len(saved_file) > 0, f"Driving book in saved excel is 0 length"
    assert (
        saved_file.loc[0, "Start Tidspunkt"]
        == results.get("result", {}).get("driving_book")[0]["start_time"]
    ), "Saved start of first trip does not match request"
