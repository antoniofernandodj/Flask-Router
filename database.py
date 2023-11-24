from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///foo.db")

def get_session():
    return Session(engine)