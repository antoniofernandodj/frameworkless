from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, registry

from src.domain.models import Todo, User


DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


mapper_registry = registry()


from src.infra.entities.users import users_table
from src.infra.entities.todo import todos_table


mapper_registry.map_imperatively(User, users_table)
mapper_registry.map_imperatively(Todo, todos_table)


mapper_registry.metadata.create_all(bind=engine)