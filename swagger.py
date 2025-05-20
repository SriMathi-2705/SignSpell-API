# swagger.py
from flasgger import Swagger
import os

def init_swagger(app):
    yaml_path = os.path.join(os.path.dirname(__file__), 'swagger.yaml')
    Swagger(app, template_file=yaml_path)
