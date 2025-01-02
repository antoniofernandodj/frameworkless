from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infra.registry import mapper_registry
from src.infra.entities import (
    consulta_table, doenca_table, exame_table, medicamento_table, pacientes_table, tarefa_table
)
from src.domain.models import (
    Consulta, Doenca, Exame, Medicamento, Paciente, Tarefa
)

def get_engine():
    try:
        from config import settings
    except:
        from src.config import settings
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    return engine

def get_session_local():
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_mappers():
    engine = get_engine()
    try:
        mapper_registry.map_imperatively(Consulta, consulta_table)
        mapper_registry.map_imperatively(Doenca, doenca_table)
        mapper_registry.map_imperatively(Exame, exame_table)
        mapper_registry.map_imperatively(Medicamento, medicamento_table)
        mapper_registry.map_imperatively(Paciente, pacientes_table)
        mapper_registry.map_imperatively(Tarefa, tarefa_table)

        mapper_registry.metadata.create_all(bind=engine)
        print('Mappers initialized')
    except Exception as error:
        print(error)
