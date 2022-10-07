import sqlalchemy
# from sqlalchemy import orm
import base64
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, SerializerMixin):
    """Класс таблицы для пользователя в БД"""
    __tablename__ = 'users'
    # serialize_rules = ('-orm_boats',)
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    discord_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    words = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    weights = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    images = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    # orm_boats = orm.relation("CapsToBoats", back_populates="captain")
