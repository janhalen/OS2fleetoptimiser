import json

import click
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import sessionmaker

from fleetmanager.data_access.db_engine import engine_creator
from fleetmanager.data_access.dbschema import (
    AllowedStarts,
    Cars,
    RoundTrips,
    SimulationSettings,
    Trips,
    VehicleTypes,
    FuelTypes,
    LeasingTypes
)


@click.group()
@click.option("-db", "--db-name", envvar="DB_NAME", required=True)
@click.option("-pw", "--password", envvar="DB_PASSWORD", required=True)
@click.option("-u", "--db-user", envvar="DB_USER", required=True)
@click.option("-l", "--db-url", envvar="DB_URL", required=True)
@click.option("-dbs", "--db-server", envvar="DB_SERVER", required=True)
@click.pass_context
def cli(ctx, db_name=None, password=None, db_user=None, db_url=None, db_server=None):
    """
    Preserves the context for the remaining functions
    Parameters
    ----------
    ctx
    db_name
    password
    db_user
    db_url
    db_server
    """
    ctx.ensure_object(dict)
    engine = engine_creator(
        db_name=db_name,
        db_password=password,
        db_user=db_user,
        db_url=db_url,
        db_server=db_server,
    )
    ctx.obj["engine"] = engine
    ctx.obj["Session"] = sessionmaker(engine)()


@cli.command()
@click.pass_context
@click.option("-p", "--path", required=True)
@click.option("-l", "--add-locations", default=False)
def add_meta_data(ctx, path, add_locations):
    """
    Method to assist the addition of metadata to the Cars table in the database.
    It's a prerequesite to have the table filled with at least id objects in the table. The path is expected to be a
    path to the excel meta data sheet. The sheet should contain "id" in order to map the vehicle to the cars table.
    Important to notice if the wltp fields and capacity_decrease field in fact is the 6th-8th index of the pandas frame.
    Remember to include the "hidden" "index" field in your counting. I.e.:
            Pandas(Index=0, registreringsnummer='xx', mærke='xx ', model='xx', køretøjstype='elbil',
                drivmiddel='xx', _6=nan, _7=x, _8=x, co2_pr_km=nan, rækkevidde=x, omkostning_aar=x,
                lokation='x', start_leasing=datetime, end_leasing=NaT, leasing_type='x', km_aar=nan, opladningstid=x)

    The object types; leasing_type, fuel, type, location will be mapped according to their respective table in the
    database.

    path : str. excel sheet of meta-data, with all the variables from the below mapper. Expects an "id"-column
    add_locations: bool. whether the locations from the sheet should be added to the vehicle. Important to notice that
        the entered string should match exactly a location in the AllowedStarts table.

    """

    # get the session
    session = ctx.obj["Session"]

    # from meta-data to schema mapping
    mapper = {
        "registreringsnummer": "plate",
        "mærke": "make",
        "model": "model",
        "køretøjstype": "type",
        "drivmiddel": "fuel",
        "_6": "wltp_fossil",
        "_7": "wltp_el",
        "_8": "capacity_decrease",
        "co2_pr_km": "co2_pr_km",
        "rækkevidde": "range",
        "omkostning_aar": "omkostning_aar",
        "lokation": "location",
        "start_leasing": "start_leasing",
        "end_leasing": "end_leasing",
        "leasing_type": "leasing_type",
        "km_aar": "km_aar",
        "opladningstid": "sleep",
        "afdeling": "department"
    }

    # models used to map object types
    object_to_default_mappings = {
        "fuel": FuelTypes,
        "leasing_type": LeasingTypes,
        "type": VehicleTypes,
        "location": AllowedStarts
    }
    session.rollback()
    # read the excel sheet
    excel = pd.read_excel(path)

    # iterate over the vehicles
    for vehicle in excel.itertuples():
        # continue if the current vehicle has no entered id
        # if pd.isna(vehicle.id) or vehicle.id < 282120:
        #     continue
        print("vehicle.id", vehicle.id)
        # get the vehicle object from the table
        car_in_db = session.get(Cars, int(vehicle.id))
        # car_in_db = session.query(Cars).filter(Cars.id == int(vehicle.id)).first()
        if car_in_db is None:
            continue

        for excel_key, schema_key in mapper.items():
            try:
                value = getattr(vehicle, excel_key)
            except AttributeError:
                value = getattr(vehicle, schema_key)

            # continue if the value is nan/none or the key is location and we shouldn't add
            if pd.isna(value) or (schema_key == 'location' and add_locations is False):
                continue

            # strip the plate value to adhere to format
            if schema_key == 'plate':
                value = value.replace(" ", "")[:7]

            if schema_key in ["fuel", "type", "leasing_type", "location"]:
                model = object_to_default_mappings[schema_key]

                if schema_key == 'location':
                    value = session.query(model).filter(model.address == value).first()
                elif type(value) != str:
                    value = session.query(model).filter(model.id == int(value)).first()
                else:
                    value = session.query(model).filter(model.name == value).first()

                if value is None:
                    continue
                if schema_key in ["fuel", "type"]:
                    value = value.refers_to
                else:
                    value = value.id
                if schema_key and 'leasing_type' and str(value) in ["1", "2"] and pd.isna(getattr(vehicle, "end_leasing")):
                    # we don't want to add a leasing type if don't have the end date for 2 and 1
                    continue

                setattr(car_in_db, schema_key + '_obj', session.get(object_to_default_mappings[schema_key], value))

            if schema_key in ['end_leasing', 'start_leasing'] and type(value) == str:
                value = datetime.strptime(value, "%d-%m-%Y")

            setattr(car_in_db, schema_key, value)
            session.commit()


@cli.command()
@click.pass_context
@click.option("-p", "--path", required=True)
@click.option(
    "-s",
    "--schema",
    required=True,
    type=click.Choice(
        ["cars", "roundtrips", "simulationsettings", "allowedstarts", "trips"]
    ),
)
def set_items(ctx, path, schema):
    Session = ctx.obj["Session"]
    extension = path.split(".")[-1]
    if extension == "csv":
        data = pd.read_csv(path, sep="\t").to_dict("records")
    elif extension == "json":
        data = json.load(open(path, "r"))
    else:
        print("Only support .csv tab delimited and json files")
        return
    schema = {
        "cars": Cars,
        "roundtrips": RoundTrips,
        "simulationsettings": SimulationSettings,
        "allowedstarts": AllowedStarts,
        "trips": Trips,
    }[schema]

    if schema == SimulationSettings:
        from fleetmanager.data_access.dbschema import get_default_simulation_settings

        ids = [a["id"] for a in get_default_simulation_settings()]
        data = [a for a in data if a["id"] not in ids]
    with Session() as s:
        items = []
        for item in data:
            items.append(
                schema(
                    **{
                        key: None if pd.isna(value) else value
                        for key, value in item.items()
                        if key in schema.__dict__.keys()
                    }
                )
            )
        max_add_pr_commit = 10000
        if len(items) > max_add_pr_commit:
            for sequence in range(0, len(items), max_add_pr_commit):
                s.add_all(items[sequence : sequence + max_add_pr_commit])
                s.commit()
                print(f"Added {max_add_pr_commit} items to the DB")
        else:
            s.add_all(items)
            s.commit()
            print(f"Added {len(items)} items to the DB")


if __name__ == "__main__":
    cli()
