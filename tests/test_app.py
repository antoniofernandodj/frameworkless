from datetime import date, datetime, timedelta
import json
from secrets import token_urlsafe
import unittest


from src.domain.models import (
    Doenca,
    Paciente,
    Exame,
    Consulta,
    Tarefa,
    Medicamento
)

from src.exceptions.http import NotFoundError, UnauthorizedError
from tests.mock import TestClient
from src import App


PACIENTE_DATA = dict(
    nome='teste',
    login='teste',
    password='password',
    data_nascimento=date(1, 1, 1),
    sexo='M',
    contato=None,
    endereco=None,
    responsavel=None,
)

def get_paciente():
    return Paciente(**PACIENTE_DATA)  # type: ignore


class Test_1_App(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        app = App(mode='test')
        cls.client = TestClient(app)
        cls.token = ''

    async def test_1_app(self):
        self.assertEqual(self.client.app.mode, 'test')

    async def test_2_settings(self):
        from src.config import settings
        self.assertEqual(settings.mode, 'TEST')

    async def test_3_controller_1(self):
        response = await self.client.get(
            path='/teste/',
            headers={'content-type': 'application/json'},
            body=None,
            query_string=''
        )
        self.assertEqual(response.status, 200)

    async def test_4_controller_2(self):
        response = await self.client.get(
            path='/teste/1/',
            headers={'content-type': 'application/json'},
            body=None,
            query_string='teste=1'
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body, json.dumps({'id': 1}))

    async def test_5_controller_3(self):
        response = await self.client.get(
            path='/teste/1/teste/2/',
            headers={'content-type': 'application/json'},
            body=None,
            query_string='teste=1'
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body, json.dumps({'arg1': 1, 'arg2': 2}))

    async def test_6_controller_4(self):
        response = await self.client.get(
            path='/teste/hello/antonio/',
            headers={'content-type': 'application/json'},
            body=None,
            query_string='key1=value1&key2=value2'
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body, json.dumps({'name': 'antonio'}))

    async def test_7_controller_5(self):
        token = token_urlsafe(10)
        response = await self.client.post(
            path=f'/teste/login/{token}/',
            headers={'content-type': 'application/json'},
            body=dict(user_id=10),
            query_string='key1=value1&key2=value2'
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(
            response.body,
            json.dumps({
                'token': token,
                'user_id': 10,
                'query': {
                    'key1': 'value1',
                    'key2': 'value2'
                }
            })
        )


class Test_2_Auth(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        app = App(mode='test')
        cls.client = TestClient(app)
        cls.data = {}

    async def auth_headers(self):
        response = await self.client.post(
            path='/auth/login/',
            headers={'content-type': 'application/json'},
            body=dict(
                login='teste',
                password='password'
            ),
            query_string='teste=1'
        )

        body = json.loads(response.body)
        token = body['token']

        return {
            'content-type': 'application/json',
            'Authorization': token
        }

    async def test_1_sign_in(self):
        response = await self.client.post(
            path='/auth/signin/',
            headers={'content-type': 'application/json'},
            body=get_paciente().to_dict(),
            query_string='teste=1'
        )

        body = json.loads(response.body)
        PACIENTE_DATA['_id'] = body['id']
        self.assertEqual(response.status, 201)

    async def test_3_auth_data(self):
        response = await self.client.post(
            path='/auth/login/',
            headers=await self.auth_headers(),
            body=dict(
                login='teste',
                password='password'
            ),
            query_string='teste=1'
        )

        body = json.loads(response.body)

        self.assertEqual(body['nome'], 'teste')

    async def test_4_invalid_login(self):
        with self.assertRaises(NotFoundError):
            await self.client.post(
                path='/auth/login/',
                headers={'content-type': 'application/json'},
                body=dict(login='invalid', password='password'),
                query_string=''
            )

    async def test_5_invalid_password(self):
        with self.assertRaises(UnauthorizedError):
            await self.client.post(
                path='/auth/login/',
                headers={'content-type': 'application/json'},
                body=dict(login='teste', password='wrong'),
                query_string=''
            )


class Test_3_Fluxo(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        app = App(mode='test')
        cls.client = TestClient(app)
        cls.data = {}

    async def auth_headers(self):
        response = await self.client.post(
            path='/auth/login/',
            headers={'content-type': 'application/json'},
            body=dict(
                login='teste',
                password='password'
            ),
            query_string='teste=1'
        )

        body = json.loads(response.body)
        token = body['token']

        return {
            'content-type': 'application/json',
            'Authorization': token
        }

    async def test_1_cadastrar_doencas(self):

        p = get_paciente()
        doenca = Doenca(
            nome='gripe',
            descricao='gripe',
            codigo_cid='1',
            paciente_id=p.id
        )

        response = await self.client.post(
            path='/doencas/',
            headers=await self.auth_headers(),
            body=doenca.to_dict(),
            query_string=''
        )

        body = json.loads(response.body)
        self.assertEquals(response.status, 201)
        self.assertIsNotNone(body)

        body['_id'] = body.pop('id')
        self.data['doenca'] = Doenca(**body)

    async def test_2_atualizar_doenca(self):
        self.data['doenca'].nome = 'resfriado'

        response = await self.client.put(
            path=f'/doencas/{self.data["doenca"].id}',
            headers=await self.auth_headers(),
            body=self.data['doenca'].to_dict(),
            query_string=''
        )

        body = json.loads(response.body)
        body['_id'] = body.pop('id')
        d = Doenca(**body)

        self.assertEquals(response.status, 200)
        self.assertEquals(d.nome, self.data['doenca'].nome)

    async def test_3_remover_doenca(self):
        response = await self.client.delete(
            path=f'/doencas/{self.data["doenca"].id}',
            headers=await self.auth_headers(),
            body=self.data['doenca'].to_dict(),
            query_string=''
        )

        body = json.loads(response.body)
        self.assertEquals(response.status, 204)
        self.assertEquals(body, None)
        self.data.pop('doenca')

    async def test_4_criar_exames(self):
        p = get_paciente()

        exame = Exame(
            tipo="Raio-X",
            data=date.today(),
            marcado=True,
            resultado=None,
            laboratorio="Laboratório Central",
            consulta_id=None,
            paciente_id=p.id
        )

        response = await self.client.post(
            path='/exames/',
            headers=await self.auth_headers(),
            body=exame.to_dict(),
            query_string=''
        )

        body = json.loads(response.body)
        self.assertEqual(response.status, 201)

        body['_id'] = body.pop('id')
        self.data['exame'] = Exame(**body)

    async def test_5_marcar_exame(self):

        exame = self.data['exame']

        response = await self.client.patch(
            path=f'/exames/{exame.id}/marcar',
            headers=await self.auth_headers(),
            body=None,
            query_string=''
        )

        body = json.loads(response.body)
        body['_id'] = body.pop('id')
        exame = Exame(**body)
        self.assertEquals(response.status, 200)
        self.assertTrue(exame.marcado)

        self.data['exame'] = Exame(**body)

    async def test_7_criar_consultas(self):
        p = get_paciente()
        consulta = Consulta(
            horario=datetime.now(),
            medico="Dr. Silva",
            paciente_id=p.id,
            motivo="Consulta de rotina",
        )

        response = await self.client.post(
            path='/consultas/',
            headers=await self.auth_headers(),
            body=consulta.to_dict(),
            query_string=''
        )

        body = json.loads(response.body)
        self.assertEqual(response.status, 201)

        body['_id'] = body.pop('id')
        self.data['consulta'] = Consulta(**body)

    async def test_8_marcar_consulta(self):
        consulta = self.data['consulta']

        response = await self.client.patch(
            path=f'/consultas/{consulta.id}/marcar',
            headers=await self.auth_headers(),
            body=None,
            query_string=''
        )

        body = json.loads(response.body)
        body['_id'] = body.pop('id')
        consulta = Consulta(**body)
        self.assertEqual(response.status, 200)
        self.assertTrue(consulta.marcado)

        self.data['consulta'] = consulta

    # TODO
    # async def test_10_criar_tarefas(self):
        # response = await self.client.post(
        #     path='',
        #     headers=await self.auth_headers(),
        #     body=dict(

        #     ),
        #     query_string=''
        # )

        # body = json.loads(response.body)

    # TODO
    # async def test_11_atualizar_tarefas(self):
    #     response = await self.client.post(
    #         path='',
    #         headers=await self.auth_headers(),
    #         body=dict(

    #         ),
    #         query_string=''
    #     )

    #     body = json.loads(response.body)

    # TODO
    # async def test_12_remover_tarefa(self):
    #     response = await self.client.post(
    #         path='',
    #         headers=await self.auth_headers(),
    #         body=dict(

    #         ),
    #         query_string=''
    #     )

    #     body = json.loads(response.body)

    # FIXME: fim_tratamento não funcionando na validação
    async def test_13_registrar_medicamentos(self):
        # breakpoint()
        medicamento = Medicamento(
            nome="Paracetamol",
            dosagem="500mg",
            frequencia="8 em 8 horas",
            inicio_tratamento=date.today(),
            # fim_tratamento=date.today() + timedelta(days=7),
            paciente_id=get_paciente().id
        )

        response = await self.client.post(
            path='/medicamentos/',
            headers=await self.auth_headers(),
            body=medicamento.to_dict(),
            query_string=''
        )

        body = json.loads(response.body)
        self.assertEqual(response.status, 201)

        body['_id'] = body.pop('id')
        self.data['medicamento'] = Medicamento(**body)

    async def test_14_atualizar_medicamento(self):
        self.data['medicamento'].frequencia = "12 em 12 horas"

        response = await self.client.put(
            path=f'/medicamentos/{self.data["medicamento"].id}',
            headers=await self.auth_headers(),
            body=self.data['medicamento'].to_dict(),
            query_string=''
        )

        body = json.loads(response.body)
        body['_id'] = body.pop('id')
        medicamento = Medicamento(**body)

        self.assertEqual(response.status, 200)
        self.assertEqual(medicamento.frequencia, self.data['medicamento'].frequencia)


    # TODO
    async def test_15_remover_medicamento(self):
        response = await self.client.delete(
            path=f'/medicamentos/{self.data["medicamento"].id}',
            headers=await self.auth_headers(),
            body=None,
            query_string=''
        )

        self.assertEqual(response.status, 204)
        self.data.pop('medicamento')
