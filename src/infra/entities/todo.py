from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, String
from src.infra.database import mapper_registry


todos_table = Table(
    'todos',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('task', String, index=True)
)
