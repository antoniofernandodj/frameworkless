from src.infra.registry import mapper_registry
from sqlalchemy import (
    Table, Column, Integer, String, Date, ForeignKey, Text, Float, create_engine, MetaData
)

metadata = mapper_registry.metadata


medicamento_table = Table(
    "medicamentos",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("nome", String(255), nullable=False),
    Column("dosagem", String(50), nullable=False),
    Column("frequencia", String(50), nullable=False),
    Column("via", String(50), nullable=True),
    Column("inicio_tratamento", Date, nullable=False),
    Column("fim_tratamento", Date, nullable=True),
    Column("paciente_id", Integer, ForeignKey("pacientes.id"), nullable=False),
    Column("doenca_id", Integer, ForeignKey("doencas.id"), nullable=True),
)