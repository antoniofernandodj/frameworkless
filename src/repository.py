from typing import Any, List, Optional, Dict, Type, TypeVar, Generic, Union
from sqlalchemy.orm import Session


T = TypeVar('T')


class GenericRepository(Generic[T]):

    model: T

    def __init__(self, session: Session) -> None:
        self.db = session

    def get_by_id(self, user_id: int) -> Optional[T]:
        return self.db.query(self.model).filter_by(id=user_id).first() # type: ignore

    def get_all(self) -> List[T]:
        return self.db.query(self.model).all() # type: ignore

    def create(self, item: T) -> T:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update(self, id: int, data: dict[str, Any]) -> Optional[T]:
        item = self.get_by_id(id)
        if not item:
            return None
        
        for key, value in data.items():
            setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, id: int) -> bool:
        item = self.get_by_id(id)
        if not item:
            return False
        self.db.delete(item)
        self.db.commit()
        return True
    

from src.domain.models import (
    Consulta, Doenca, Exame, Medicamento, Paciente, Tarefa
)


# Repository para Paciente
class PacienteRepository(GenericRepository[Paciente]):
    model = Paciente # type: ignore


# Repository para Consulta
class ConsultaRepository(GenericRepository[Consulta]):
    model = Consulta # type: ignore


# Repository para Doença
class DoencaRepository(GenericRepository[Doenca]):
    model = Doenca # type: ignore


# Repository para Exame
class ExameRepository(GenericRepository[Exame]):
    model = Exame # type: ignore


# Repository para Medicamento
class MedicamentoRepository(GenericRepository[Medicamento]):
    model = Medicamento # type: ignore


# Repository para Tarefa
class TarefaRepository(GenericRepository[Tarefa]):
    model = Tarefa # type: ignore