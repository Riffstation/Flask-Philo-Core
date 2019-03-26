from flask import current_app
from flask_philo_core import init_app
from decimal import Decimal
from unittest.mock import Mock, patch

import os
import random
import string
import sys
import uuid


BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class FlaskPhiloTestCase(object):
    config = {}
    urls = ()

    """
    This tests should be used when testing views
    """
    json_request_headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    def setup(self):
        try:
            self.app = current_app._get_current_object()
            self.app.logger.debug('Retreive app {}'.format(self.app))
        except Exception:
            self.app = BaseTestFactory.create_test_app(
                config=self.config, urls=self.urls)
            self.app.logger.debug('Create app {}'.format(self.app))


class BaseTestFactory(object):
    @classmethod
    def create_test_app(cls, config=None, urls=None):
        config_mock = Mock()
        sys_modules_mock = {}

        if config is not None:
            for k, v in config.items():
                setattr(config_mock, k, v)

        if urls is not None:
            config_mock.URLS = 'app.urls'
            url_mock = Mock()
            url_mock.URLS = urls
            sys_modules_mock['app.urls'] = url_mock

        sys_modules_mock['config.settings'] = config_mock
        with patch.dict(sys.modules, sys_modules_mock):
            with patch.dict(
                os.environ, {
                    'FLASK_PHILO_SETTINGS_MODULE': 'config.settings'}):
                return init_app(__name__)

    @classmethod
    def create_uuid(cls):
        return uuid.uuid4()

    @classmethod
    def create_unique_string(cls, prefix=None, n_range=20):
        st = ''.join(
            random.choice(
                string.ascii_lowercase + string.digits)
            for x in range(n_range))

        if prefix:
            return '{0}-{1}'.format(prefix, st)
        else:
            return '{0}'.format(st)

    @classmethod
    def create_unique_email(cls):
        return '{0}@{1}.com'.format(
            cls.create_unique_string(), cls.create_unique_string())

    @classmethod
    def create_random_decimal(cls, n=10000):
        return Decimal((random.randrange(n)/100))
