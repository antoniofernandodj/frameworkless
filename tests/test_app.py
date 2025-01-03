from datetime import date
import json
from secrets import token_urlsafe
import unittest


from tests.mock import TestClient
from src import App



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
            path='/hello/antonio/',
            headers={'content-type': 'application/json'},
            body=None,
            query_string='key1=value1&key2=value2'
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body, json.dumps({'name': 'antonio'}))

    async def test_7_controller_5(self):
        token = token_urlsafe(10)
        response = await self.client.post(
            path=f'/test/login/{token}/',
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
            path='/login/',
            headers={'content-type': 'application/json'},
            body=dict(
                login='teste',
                password='senha'
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
            path='/signin/',
            headers={'content-type': 'application/json'},
            body=dict(
                nome='teste',
                login='teste',
                password='senha',
                data_nascimento=date(1, 1, 1).isoformat(),
                sexo='M',
                contato=None,
                endereco=None,
                responsavel=None,
            ),
            query_string='teste=1'
        )
        self.assertEqual(response.status, 201)

    async def test_3_auth_data(self):
        response = await self.client.post(
            path='/login/',
            headers=self.auth_headers(),
            body=dict(
                login='teste',
                password='senha'
            ),
            query_string='teste=1'
        )

        body = json.loads(response.body)

        self.assertEqual(body['nome'], 'teste')


class Test_3_Fluxo(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        app = App(mode='test')
        cls.client = TestClient(app)
        cls.data = {}

    async def auth_headers(self):
        response = await self.client.post(
            path='/login/',
            headers={'content-type': 'application/json'},
            body=dict(
                login='teste',
                password='senha'
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
        response = await self.client.post(
            path='',
            headers=self.auth_headers(),
            body=dict(

            ),
            query_string=''
        )

        body = json.loads(response.body)

    async def test_2_atualizar_doenca(self):
        response = await self.client.post(
            path='',
            headers=self.auth_headers(),
            body=dict(

            ),
            query_string=''
        )

        body = json.loads(response.body)

    async def test_3_remover_doenca(self):
        response = await self.client.post(
            path='',
            headers=self.auth_headers(),
            body=dict(

            ),
            query_string=''
        )

        body = json.loads(response.body)

    async def test_4_criar_exames(self):
        response = await self.client.post(
            path='',
            headers=self.auth_headers(),
            body=dict(

            ),
            query_string=''
        )

        body = json.loads(response.body)

    async def test_5_marcar_exame(self):
        response = await self.client.post(
            path='',
            headers=self.auth_headers(),
            body=dict(

            ),
            query_string=''
        )

        body = json.loads(response.body)

    async def test_6_arquivar_resultado_de_exame(self):
        response = await self.client.post(
            path='',
            headers=self.auth_headers(),
            body=dict(

            ),
            query_string=''
        )

        body = json.loads(response.body)

    async def test_7_criar_consultas(self):
        response = await self.client.post(
            path='',
            headers=self.auth_headers(),
            body=dict(

            ),
            query_string=''
        )

        body = json.loads(response.body)

    async def test_8_marcar_consulta(self):
        response = await self.client.post(
            path='',
            headers=self.auth_headers(),
            body=dict(

            ),
            query_string=''
        )

        body = json.loads(response.body)

    async def test_9_arquivar_resultado_de_consulta(self):
        response = await self.client.post(
            path='',
            headers=self.auth_headers(),
            body=dict(

            ),
            query_string=''
        )

        body = json.loads(response.body)

    async def test_10_criar_tarefas(self):
        response = await self.client.post(
            path='',
            headers=self.auth_headers(),
            body=dict(

            ),
            query_string=''
        )

        body = json.loads(response.body)

    async def test_11_atualizar_tarefas(self):
        response = await self.client.post(
            path='',
            headers=self.auth_headers(),
            body=dict(

            ),
            query_string=''
        )

        body = json.loads(response.body)

    async def test_12_remover_tarefa(self):
        response = await self.client.post(
            path='',
            headers=self.auth_headers(),
            body=dict(

            ),
            query_string=''
        )

        body = json.loads(response.body)

    async def test_13_registrar_medicamentos(self):
        response = await self.client.post(
            path='',
            headers=self.auth_headers(),
            body=dict(

            ),
            query_string=''
        )

        body = json.loads(response.body)

    async def test_14_atualizar_medicamento(self):
        response = await self.client.post(
            path='',
            headers=self.auth_headers(),
            body=dict(

            ),
            query_string=''
        )

        body = json.loads(response.body)

    async def test_15_remover_medicamento(self):
        response = await self.client.post(
            path='',
            headers=self.auth_headers(),
            body=dict(

            ),
            query_string=''
        )

        body = json.loads(response.body)
