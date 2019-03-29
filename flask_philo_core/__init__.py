from flask import Flask
from . import default_settings
from . import philo_commands
from .exceptions import ConfigurationError
from .logger import init_logging

import argparse
import importlib
import os
import sys


__version__ = '0.5.0'


class GenericSingleton:
    """
    Singleton pattern
    """
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class Plugins(GenericSingleton):
    def __init__(self):
        super(Plugins, self).__init__()
        self.flask_philo_sqlalchemy = None


class PhiloFlask(Flask):
    plugins = Plugins()


def init_urls(app):
    if 'URLS' in app.config:
        # URLS is a tuple of dictionary, every dictionary represent a rule
        # http://flask.pocoo.org/docs/0.12/api/#flask.Flask.add_url_rule
        urls_module = importlib.import_module(app.config['URLS'])
        for record in urls_module.URLS:
            route = record.copy()
            if 'rule' in route:
                rule = route.pop('rule')
                app.add_url_rule(rule, **route)


def init_cors(app):
    """
    Initializes cors protection if config
    """
    if 'CORS' in app.config:
        from flask_cors import CORS
        CORS(app, resources=app.config['CORS'])


def init_config(app):
    """
    Load settings module and attach values to the application
    config dictionary
    """
    if 'FLASK_PHILO_SETTINGS_MODULE' not in os.environ:
        raise ConfigurationError('No settings has been defined')

    # Flask-Philo-Core default configuration values are
    # appended to the app configuration
    for v in dir(default_settings):
        app.config[v] = getattr(default_settings, v)

    # Append configuration defined in settings file to the app
    settings = importlib.import_module(
        os.environ['FLASK_PHILO_SETTINGS_MODULE'])

    for v in dir(settings):
        app.config[v] = getattr(settings, v)


def init_dbs(app):
    """
    Initializes database configurations if extensions
    are included
    """
    if 'Flask-Philo-SQLAlchemy' in app.config['FLASK_PHILO_EXTENSIONS']:
        from flask_philo_sqlalchemy.connection import create_pool
        with app.app_context():
            create_pool()


def init_app(module):
    """
    Initalize an app, call this method once from start_app
    Implements Application Factory concept described at
    http://flask.pocoo.org/docs/1.0/patterns/appfactories/#app-factories
    """
    app = PhiloFlask(module)
    init_config(app)
    init_logging(app)
    init_urls(app)
    init_cors(app)
    init_dbs(app)
    return app


def execute_command(cmd, **kwargs):
    """
    execute a console command
    """
    cmd_dict = {}
    for cm in philo_commands.__all__:
        if not cm.startswith('_'):
            cmd_dict[cm] = 'flask_philo_core.philo_commands.' + cm

    # loading specific app commands
    try:
        import commands
        for cm in commands.__all__:
            if not cm.startswith('_'):
                cmd_dict[cm] = 'commands.' + cm
    except Exception:
        pass

    if cmd not in cmd_dict:
        raise ConfigurationError('command {} does not exists'.format(cmd))

    cmd_module = importlib.import_module(cmd_dict[cmd])
    cmd_module.run()


def run():
    BASE_DIR = os.getcwd()
    sys.path.append(os.path.join(BASE_DIR, './'))

    description = 'Manage Flask-Philo application'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('command', help='command to execute')
    parser.add_argument(
        '--settings', help='config file path', default='config.settings')

    args, extra_params = parser.parse_known_args()
    os.environ.setdefault('FLASK_PHILO_SETTINGS_MODULE', args.settings)

    app = init_app(__name__)

    with app.app_context():
        execute_command(args.command)


def philo_app(f, *args, **kwargs):
    def new_f(*args, **kwargs):
        app = init_app(__name__)
        with app.app_context():
            return f(*args, **kwargs)
    return new_f
