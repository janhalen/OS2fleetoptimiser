from typing import Any, Generator
from fleetmanager.data_access.db_engine import engine_creator
from pydantic import BaseModel
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyCookie
import os
from sqlalchemy.orm import sessionmaker, Session

engine = engine_creator()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Generator[Session, Any, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.flush()
        db.expunge_all()
        db.close()
