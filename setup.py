from setuptools import setup


long_version = """
Flask extension that provides a common framework out of the box for
builing RESTful microservices. It integrates a common structure for
flask projects, json validation and unit testing.
"""


setup(
    name='Flask-Philo-Core',
    version='0.5.0',
    description='Flask extension that provides a common framework for webapps',
    long_description='',
    packages=[
        'flask_philo_core', 'flask_philo_core.philo_commands',
        'flask_philo_core.admin', 'flask_philo_core.admin.templates',
        'flask_philo_core.admin.templates.project',
    ],
    package_data={
        'flask_philo_core.admin.templates.project': ['*']
    },
    url='https://github.com/Riffstation/flask-philo',
    author='Manuel Ignacio Franco Galeano',
    author_email='maigfrga@gmail.com',
    license='Apache',
    install_requires=[
        'Flask>=1.0',
        'flask-cors',
        'simplejson',
        'JSON-log-formatter',
        'pytest',
        'rfc3987',
        'strict-rfc3339',
        'webcolors',
        'jsonschema',
        'aws-lambda-wsgi'
    ],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Framework :: Flask',
        'Programming Language :: Python :: 3',
    ],
    keywords='flask REST framework',
    entry_points={
        "console_scripts": [
            "flask-philo-admin = flask_philo_core.admin:main",
            "flask-philo = flask_philo_core:run",
        ]
    }
)
