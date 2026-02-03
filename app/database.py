from sqlmodel import Field, SQLModel, create_engine, Session, select
from typing import Optional
import os

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    mobile_number: str

sqlite_file_name = "users.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def save_user(name: str, mobile_number: str):
    with Session(engine) as session:
        user = User(name=name, mobile_number=mobile_number)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
