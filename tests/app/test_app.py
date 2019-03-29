from flask import current_app, json

from flask_philo_core import init_app, philo_app
from flask_philo_core.aws import aws_lambda
from flask_philo_core.exceptions import ConfigurationError
from unittest.mock import patch

import os
import pytest
import sys


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(BASE_DIR, '../'))


def test_app_creation():
    """
    Test if a Flask-Philo_Core app is created properly
    """

    # check that raises error if not settings file is provided
    with pytest.raises(ConfigurationError):
        init_app(__name__)

    with patch.dict(
        os.environ, {
            'FLASK_PHILO_SETTINGS_MODULE': 'config.settings'}):
        app = init_app(__name__)
        assert app is not None
        assert app.name == __name__


def test_app_decorator():
    """
    Test app initialization using decorator
    """

    with patch.dict(
        os.environ, {
            'FLASK_PHILO_SETTINGS_MODULE': 'config.settings'}):

        @philo_app
        def my_func(v1, v2, context=None):
            assert v1 is True
            assert 1 == v2
            assert context == 'context'
            app = current_app._get_current_object()
            assert app is not None
            return True

        assert my_func(True, 1, 'context') is True


def test_aws_lambda():

    with patch.dict(
        os.environ, {
            'FLASK_PHILO_SETTINGS_MODULE': 'config.settings'}):

        @philo_app
        @aws_lambda
        @philo_app
        def post_func_view():
            return json.dumps({'msg': 'ok'})

        result = post_func_view()
        print(result)
