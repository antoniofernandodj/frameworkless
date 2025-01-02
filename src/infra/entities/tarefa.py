from src.infra.registry import mapper_registry
from sqlalchemy import (
    Table, Column, Integer, String, Date, ForeignKey, Text, Float, create_engine, MetaData
)

metadata = mapper_registry.metadata


tarefa_table = Table(
    "tarefas",
    metadata,
    Column("_id", Integer, primary_key=True),
    Column("descricao", Text, nullable=False),
    Column("data_limite", Date, nullable=True),
    Column("status", String(50), nullable=False),
    Column("paciente_id", Integer, ForeignKey("pacientes._id"), nullable=False),
)