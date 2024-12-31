from bson import ObjectId
from typing import Any, List, Optional, Type, TypeVar, Generic
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from motor.motor_asyncio import AsyncIOMotorClient
from src.domain.models import (
    Consulta, Doenca, Exame, Medicamento, Paciente, Tarefa, DomainModel
)


T = TypeVar('T')


class GenericRepository(Generic[T]):
    model: Type[T]
    db: AsyncIOMotorDatabase
    collection_name: str

    def __init__(self, db) -> None:
        self.db = db
        self.collection: AsyncIOMotorCollection = self.db[self.collection_name]

    async def get_by_id(self, item_id: Any) -> Optional[T]:
        data = await self.collection.find_one({"_id": item_id})
        return self.model(**data) if data else None

    async def get_all(self, filters: Optional[dict] = None) -> List[T]:
        cursor = self.collection.find(filters or {})
        results = [self.model(**doc) async for doc in cursor]
        return results

    async def create(self, item: DomainModel) -> T:
        result = await self.collection.insert_one(item.to_dict())
        item_id = result.inserted_id
        result = await self.get_by_id(item_id)
        if result is None:
            raise LookupError
        
        return result

    async def update(self, item_id: Any, data: dict) -> Optional[T]:
        result = await self.collection.update_one({"_id": item_id}, {"$set": data})
        if result.modified_count == 0:
            return None
        return await self.get_by_id(item_id)

    async def delete(self, item_id: Any) -> bool:
        result = await self.collection.delete_one({"_id": item_id})
        return result.deleted_count > 0




class PacienteRepository(GenericRepository[Paciente]):
    model = Paciente
    collection_name = "pacientes"


class ConsultaRepository(GenericRepository[Consulta]):
    model = Consulta
    collection_name = "consultas"


class DoencaRepository(GenericRepository[Doenca]):
    model = Doenca
    collection_name = "doencas"


class ExameRepository(GenericRepository[Exame]):
    model = Exame
    collection_name = "exames"


class MedicamentoRepository(GenericRepository[Medicamento]):
    model = Medicamento
    collection_name = "medicamentos"



class TarefaRepository(GenericRepository[Tarefa]):
    model = Tarefa
    collection_name = "tarefas"

