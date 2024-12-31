from sqlalchemy import Date, Text
from sqlalchemy.schema import Column, Table
from sqlalchemy.types import Integer, String
from src.infra.registry import mapper_registry


pacientes_table = Table(
    'pacientes',
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("nome", String(255), nullable=False),
    Column("data_nascimento", Date, nullable=False),
    Column("sexo", String(10), nullable=False),
    Column("contato", String(255), nullable=True),
    Column("endereco", Text, nullable=True),
    Column("responsavel", String(255), nullable=True),

)
