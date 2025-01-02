from src.infra.registry import mapper_registry
from sqlalchemy import (
    Table, Column, Integer, String, Date, ForeignKey, Text, Float, create_engine, MetaData
)

metadata = mapper_registry.metadata


doenca_table = Table(
    "doencas",
    metadata,
    Column("_id", Integer, primary_key=True),
    Column("nome", String(255), nullable=False),
    Column("descricao", Text, nullable=True),
    Column("codigo_cid", String(20), nullable=True),
    Column("paciente_id", Integer, ForeignKey("pacientes._id"), nullable=False),
)