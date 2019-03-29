from flask import current_app
# import aws_lambda_wsgi


def aws_lambda(f,  *args, **kwargs):
    def new_f(*args, **kwargs):
        app = current_app._get_current_object()
        with app.app_context():
            return f(*args, **kwargs)
    return new_f
