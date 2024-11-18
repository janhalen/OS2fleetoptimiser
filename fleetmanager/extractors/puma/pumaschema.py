from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey, func, UniqueConstraint, Float, BigInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
import uuid

Base = declarative_base()


class Materiels(Base):
    __tablename__ = 'materiels'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    type = Column(String(100))
    registreringsnummer = Column(String(20))
    center = Column(String(50))
    placeringsadresse = Column(String(50))
    placeringkode = Column(Integer)
    imeinummer = Column(String(20))
    state = Column(String(50))
    serviceomraade = Column(String(50))
    forvaltning = Column(String(25))
    systemstatus = Column(String(25))
    maskingruppe = Column(String(25))
    stelnummer = Column(String)
    nummer = Column(Integer, nullable=True)
    lastupdated = Column(DateTime, nullable=True)


class Data(Base):
    __tablename__ = 'data'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    imei = Column(String(20), nullable=False)
    timestamp = Column(DateTime)
    coords = Column(Geometry(geometry_type='POINT', srid=4326))
    speed = Column(Integer)
    angle = Column(Float)
    altitude = Column(Float)
    satellites = Column(Integer)
    hdop = Column(Integer)
    initiatedby = Column(Integer)
    ignition = Column(Boolean)
    gsm = Column(Integer)
    digitalinput1 = Column(Boolean)
    digitalinput2 = Column(Boolean)
    currentprofile = Column(Integer)
    temperature = Column(Integer)
    movement = Column(Boolean)
    sleeptimer = Column(Boolean)
    powersupplyvoltage = Column(Float)
    batteryvoltage = Column(Float)
    analoginput1 = Column(Integer)
    analoginput2 = Column(Integer)
    odometertotal = Column(Integer)
    operatorid = Column(Integer)
    accelerometerx = Column(Float)
    accelerometery = Column(Float)
    accelerometerz = Column(Float)
    ibuttonid = Column(Integer)
    digitalinput1hours = Column(Integer)
    digitalinput2hours = Column(Integer)
    digitalinput3hours = Column(Integer)
    ignitionhours = Column(Integer)
    geofencing = Column(Integer)
    speedsensor = Column(Integer)
    receivedat = Column(DateTime)
    materielid = Column(UUID(as_uuid=True))
    sourceprotocol = Column(String(25), default='Ruptela')
    importbatchid = Column(Integer)
    timestampext = Column(Integer)
    odometerdiff = Column(Integer)
    ignitionhourstotal = Column(Integer)
    digitalinput1hourstotal = Column(Integer)
    digitalinput2hourstotal = Column(Integer)

    def get_coordinates(self):
        """
        returns latitude longitude
        """
        if self.coords:
            coordinates = to_shape(self.coords)
            return coordinates.y, coordinates.x
        return None
