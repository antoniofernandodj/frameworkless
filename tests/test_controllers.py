from datetime import date
import unittest

from src.controllers.teste import TesteController
from tests.mock import make_controller_request
from src.repository import PacienteRepository
from src.domain.models import Paciente
from src.infra.database.sql import get_session_local


class TestRepos(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.controller = TesteController()
        SessionLocal = get_session_local()
        session = SessionLocal()
        cls.repo = PacienteRepository(session)

    async def test_repos(self):

        paciente0 = self.repo.create(
            Paciente('antonio', 'login', 'senha', date(1, 2, 3), 'M')
        )
        print(paciente0)
        paciente1 = self.repo.get_by_id(1)
        assert paciente1
        paciente1.update_from_dict({'nome': 'Antonio Fernando'})
        paciente2 = self.repo.get_by_id(1)
        assert paciente2
        print(paciente2)
        self.repo.delete(paciente2.id)
        paciente3 = self.repo.get_by_id(1)
        assert paciente3 is None
        print(paciente3)


class TestControllers(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        cls.controller = TesteController()

    async def test_controller_1(self):
        request = make_controller_request(query={}, body={}, headers={})
        result = await self.controller.teste_endpoint_1(request)
        self.assertEqual(result.status, 200)

    async def test_controller_2(self):
        request = make_controller_request(query={}, body={}, headers={})
        result = await self.controller.teste_endpoint_2(request, id=1)
        self.assertEqual(result.body, {'id': 1})


