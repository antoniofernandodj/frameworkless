# src/services/consulta_service.py

from src.repository import ConsultaRepository
from src.domain.models import Consulta


class ConsultaService:

    def __init__(self, consulta_repository: ConsultaRepository) -> None:
        self.consulta_repository = consulta_repository

    def get_repository(self):
        return self.consulta_repository

    def get_consulta_by_id(self, consulta_id: int) -> Consulta:
        consulta = self.consulta_repository.get_by_id(consulta_id)
        if consulta is None:
            raise LookupError("Consulta não encontrada")
        return consulta

    def marcar_consulta(self, consulta_id: int) -> Consulta:
        consulta = self.consulta_repository.update(consulta_id, {"marcado": True})
        if consulta is None:
            raise LookupError("Consulta não encontrada")
        return consulta

    def update_consulta(self, consulta_id: int, body: dict) -> Consulta:
        consulta = self.consulta_repository.update(consulta_id, body)
        if consulta is None:
            raise LookupError("Consulta não encontrada")
        return consulta

    def delete_consulta(self, consulta_id: int) -> bool:
        success = self.consulta_repository.delete(consulta_id)
        if not success:
            raise LookupError("Consulta não encontrada")
        return success
