import click
from sqlalchemy.orm import sessionmaker
from fleetmanager.extractors.clevertrack.updatedb import cli, set_vehicles
from fleetmanager.data_access import engine_creator


cont = click.Context(cli)
cont.ensure_object(dict)
cont.obj["headers"] = {}


engine = engine_creator(
    db_name="",
    db_password="",
    db_server="mssql+pyodbc",
    db_user="",
    db_url="",
)

cont.obj["token"] = ""

cont.obj["Session"] = sessionmaker(bind=engine)

cont.obj["engine"] = engine

print(cont.obj, flush=True)

cont.invoke(set_vehicles, description_fields="name")
