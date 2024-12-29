from sqlalchemy.schema import Column, Table
from sqlalchemy.types import Integer, String
from src.infra.database import mapper_registry


users_table = Table(
    'users',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('name', String, index=True)

)
