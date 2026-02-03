from sqlmodel import Field, SQLModel, create_engine, Session, select
from typing import Optional
import os

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    mobile_number: str

sqlite_file_name = "users.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Use DATABASE_URL from environment for production (e.g., Vercel Postgres)
# Default to local SQLite if not provided
database_url = os.getenv("DATABASE_URL", sqlite_url)

# SQLAlchemy/SQLModel require postgresql:// instead of postgres://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(database_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def save_user(name: str, mobile_number: str):
    with Session(engine) as session:
        user = User(name=name, mobile_number=mobile_number)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
