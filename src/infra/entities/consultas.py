from src.infra.registry import mapper_registry
from sqlalchemy import (
    Table, Column, Integer, Boolean, String, Date, ForeignKey, Text, Float, create_engine, MetaData, text
)

metadata = mapper_registry.metadata

consulta_table = Table(
    "consultas",
    metadata,
    Column("_id", Integer, primary_key=True),
    Column("data", Date, nullable=False),
    Column("marcada", Boolean, nullable=False, server_default=text('false')),
    Column("medico", String(255), nullable=False),
    Column("especialidade", String(255), nullable=True),
    Column("local", String(255), nullable=True),
    Column("observacoes", Text, nullable=True),
    Column("paciente_id", Integer, ForeignKey("pacientes._id"), nullable=False),
    Column("doenca_id", Integer, ForeignKey("doencas._id"), nullable=True),
)
