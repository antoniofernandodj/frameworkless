from src.infra.registry import mapper_registry
from sqlalchemy import (
    Table, Column, Integer, String, Date, Boolean, ForeignKey, Text, Float, create_engine, MetaData, text
)

metadata = mapper_registry.metadata


exame_table = Table(
    "exames",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("tipo", String(255), nullable=False),
    Column("data", Date, nullable=False),
    Column("marcado", Boolean, nullable=False, server_default=text('false')),
    Column("resultado", Text, nullable=True),
    Column("laboratorio", String(255), nullable=True),
    Column("consulta_id", Integer, ForeignKey("consultas.id"), nullable=True),
    Column("paciente_id", Integer, ForeignKey("pacientes.id"), nullable=False),
)