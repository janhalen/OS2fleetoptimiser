from importlib.resources import files
from uuid import uuid4

import pytest
from sqlalchemy import StaticPool, create_engine, text
from sqlalchemy.orm import sessionmaker

from fleetmanager.data_access.db_engine import create_defaults
from fleetmanager.data_access.dbschema import Base


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        f"sqlite:///file:fleetdb_{uuid4().hex}?mode=memory&cache=shared&uri=true",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)
    file = open(
        files("fleetmanager").joinpath("dummy_data.sql"), encoding="UTF-8"
    ).read()
    for a in file.split(";"):
        with sessionmaker(bind=engine)() as s:
            e = (a.replace("\n", "").replace("\t", "").replace("  ", "") + ";").strip()
            if len(e) == 1:
                continue
            s.execute(text(e))
            s.commit()
    create_defaults(engine)
    session = sessionmaker(autoflush=False, autocommit=False, bind=engine)()
    yield session
    session.close()
