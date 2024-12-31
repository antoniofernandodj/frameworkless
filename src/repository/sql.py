from typing import Any, List, Optional, Dict, Type, TypeVar, Generic, Union
from sqlalchemy.orm import Session
from src.domain.models import (
    Consulta, Doenca, Exame, Medicamento, Paciente, Tarefa
)


T = TypeVar('T')


class GenericRepository(Generic[T]):

    model: Type[T]

    def __init__(self, session: Session) -> None:
        self.db = session

    def get_by_id(self, user_id: int) -> Optional[T]:
        return self.db.query(self.model).filter_by(id=user_id).first()

    def get_all(self) -> List[T]:
        return self.db.query(self.model).all()

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



class PacienteRepository(GenericRepository[Paciente]):
    model = Paciente



class ConsultaRepository(GenericRepository[Consulta]):
    model = Consulta



class DoencaRepository(GenericRepository[Doenca]):
    model = Doenca



class ExameRepository(GenericRepository[Exame]):
    model = Exame



class MedicamentoRepository(GenericRepository[Medicamento]):
    model = Medicamento



class TarefaRepository(GenericRepository[Tarefa]):
    model = Tarefa