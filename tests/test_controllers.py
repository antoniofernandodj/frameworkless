import sys
import pathlib

sys.path.append(
    str(pathlib.Path(__file__).parent.parent.absolute())
)


from datetime import date
from typing import Any
import asyncio
import unittest

from src.controllers.teste import TesteController
from tests.utils import mock_request
from src.repository import PacienteRepository
from src.domain.models import Paciente
from src.infra.database.sql import SessionLocal


class TestRepos(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.controller = TesteController()
        session = SessionLocal()
        cls.repo = PacienteRepository(session)

    async def test_repos(self):

        paciente0 = self.repo.create(Paciente(1, 'antonio', date(1,2,3), 'F'))
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

    async def test_controller(self):
        request = mock_request(path={}, query={}, body={}, headers={})
        result = await self.controller.teste_endpoint_1(request)
        self.assertEqual(result['status'], 200)


