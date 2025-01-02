from datetime import date
import json
from secrets import token_urlsafe
import unittest


from tests.mock import make_rsgi_request, mock_request
from app import App



class TestApp(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = App(mode='test')

    async def test_app1(self):
        response = await mock_request(
            app=self.app,
            path='/teste/',
            method='GET',
            headers={'content-type': 'application/json'},
            body=None,
            query_string=''
        )
        self.assertEqual(response.status, 200)

    async def test_app2(self):
        self.assertEqual(self.app.mode, 'test')

    async def test_settings(self):
        from src.config import settings
        self.assertEqual(settings.mode, 'TEST')

    async def test_sign_in_and_login(self):
        response = await mock_request(
            app=self.app,
            path='/signin/',
            method='POST',
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

        response = await mock_request(
            app=self.app,
            path='/login/',
            method='POST',
            headers={'content-type': 'application/json'},
            body=dict(
                login='teste',
                password='senha'
            ),
            query_string='teste=1'
        )
        self.assertEqual(response.status, 200)

    async def test_controller_2(self):
        response = await mock_request(
            app=self.app,
            path='/teste/1/',
            method='GET',
            headers={'content-type': 'application/json'},
            body=None,
            query_string='teste=1'
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body, json.dumps({'id': 1}))

    async def test_controller_3(self):
        response = await mock_request(
            app=self.app,
            path='/teste/1/teste/2/',
            method='GET',
            headers={'content-type': 'application/json'},
            body=None,
            query_string='teste=1'
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body, json.dumps({'arg1': 1, 'arg2': 2}))

    async def test_controller_4(self):
        response = await mock_request(
            app=self.app,
            path='/hello/antonio/',
            method='GET',
            headers={'content-type': 'application/json'},
            body=None,
            query_string='key1=value1&key2=value2'
        )
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body, json.dumps({'name': 'antonio'}))

    async def test_controller_5(self):
        token = token_urlsafe(10)
        response = await mock_request(
            app=self.app,
            path=f'/test/login/{token}/',
            method='POST',
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
