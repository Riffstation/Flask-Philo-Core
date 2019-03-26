from flask_philo_core import philo_app
from flask_philo_core.views import BaseView
from flask_philo_core.test import FlaskPhiloTestCase, BaseTestFactory
from flask import current_app, json
from flask import request
from unittest.mock import patch

import os


class SimpleView(BaseView):
    def get(self):
        return self.json_response(data={'msg': 'ok'})

    def post(self):
        return self.json_response(data={'msg': 'ok-post'})


class SimpleCorsView(BaseView):
    def get(self):
        return self.json_response(data={'msg': 'ok-cors'})


CLASS_URLS = (
    {
        'rule': '/', 'endpoint': 'home',
        'view_func': SimpleView.as_view('home')
    },
    {
        'rule': '/cors-api/test-cors', 'endpoint': 'test_cors',
        'view_func': SimpleCorsView.as_view('cors')
    },
)


class TestClassViews(FlaskPhiloTestCase):
    def test_urls(self):
        app = BaseTestFactory.create_test_app()
        assert 'URLS' not in app.config
        rules = [r for r in app.url_map.iter_rules()]
        endpoints = [rl.endpoint for rl in rules]
        assert 1 == len(endpoints)
        assert 'static' in endpoints

        app = BaseTestFactory.create_test_app(urls=CLASS_URLS)

        assert 'URLS' in app.config
        rules2 = [r for r in app.url_map.iter_rules()]
        endpoints2 = [rl.endpoint for rl in rules2]
        assert 3 == len(endpoints2)
        assert 'test_cors' in endpoints2
        assert 'static' in endpoints2
        assert 'home' in endpoints2

    def test_simple_view(self):
        app = BaseTestFactory.create_test_app(urls=CLASS_URLS)
        client = app.test_client()
        result = client.get('/')
        assert 200 == result.status_code
        j_content = json.loads(result.get_data().decode('utf-8'))
        assert 'msg' in j_content
        assert 'ok' == j_content['msg']

        result = client.post('/')
        assert 200 == result.status_code
        j_content = json.loads(result.get_data().decode('utf-8'))
        assert 'msg' in j_content
        assert 'ok-post' == j_content['msg']

        result = client.put('/')
        assert 400 == result.status_code

    def test_cors(self):
        config = {}
        config['CORS'] = {
            r"/cors-api/*": {"origins": "FLASK_PHILO_CORE_TEST_CORS"}}
        app = BaseTestFactory.create_test_app(config=config, urls=CLASS_URLS)
        client = app.test_client()
        result = client.get('/cors-api/test-cors')
        assert 'Access-Control-Allow-Origin' in result.headers
        cors_val = result.headers['Access-Control-Allow-Origin']
        assert 'FLASK_PHILO_CORE_TEST_CORS' == cors_val
        assert 200 == result.status_code

        j_content = json.loads(result.get_data().decode('utf-8'))
        assert 'msg' in j_content
        assert 'ok-cors' == j_content['msg']


@philo_app
def simple_func_view():
    app = current_app._get_current_object()
    assert app is not None
    return json.dumps({'msg': 'ok'})


@philo_app
def post_func_view():
    return json.dumps(request.json)


VIEWS_URLS = (
    {
        'rule': '/', 'view_func': simple_func_view
    },
    {
        'rule': '/post-func', 'endpoint': 'post_endpoint',
        'view_func': post_func_view, 'methods': ['POST']
    },
)


def test_view_function():
    with patch.dict(
        os.environ, {
            'FLASK_PHILO_SETTINGS_MODULE': 'config.settings'}):
        app = BaseTestFactory.create_test_app(urls=VIEWS_URLS)
        client = app.test_client()
        result = client.get('/')
        assert 200 == result.status_code
        j_content = json.loads(result.get_data().decode('utf-8'))
        assert 'msg' in j_content
        assert 'ok' == j_content['msg']

        result = client.post('/')
        assert 405 == result.status_code


def test_post_view_function():
    with patch.dict(
        os.environ, {
            'FLASK_PHILO_SETTINGS_MODULE': 'config.settings'}):
        app = BaseTestFactory.create_test_app(urls=VIEWS_URLS)
        client = app.test_client()
        result = client.get('/post-func')
        assert 405 == result.status_code
        data = {
            'msg': 'post-data'
        }

        result = client.post(
            '/post-func', data=json.dumps(data),
            content_type='application/json')
        assert 200 == result.status_code
        j_content = json.loads(result.get_data().decode('utf-8'))
        assert 'msg' in j_content
        assert 'post-data' == j_content['msg']
