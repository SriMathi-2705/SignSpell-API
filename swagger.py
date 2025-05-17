# swagger.py
from flasgger import Swagger



swagger_template = {
    'swagger': '2.0',
    'info': {
        'title': 'User Authentication API',
        'version': '1.0.0',
        'description': 'Signup, Login, Token Refresh, Password Reset, CRUD, Logout'
    },
    'basePath': '/'
}

def init_swagger(app):
    Swagger(app, template_file='swagger.yaml')