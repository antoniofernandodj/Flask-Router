from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.types import Integer, String
from flask_login import UserMixin  # type: ignore


class Base(DeclarativeBase): ...

class User(Base, UserMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    password: Mapped[str]
