# swagger.py
from flasgger import Swagger

def init_swagger(app):
    Swagger(
        app,
        template_file='swagger.yaml',
        config={
            'headers': [],
            'specs': [
                {
                    'endpoint': 'apispec_1',
                    'route': '/apispec_1.json',
                    'rule_filter': lambda rule: True,    # include all endpoints
                    'model_filter': lambda tag: True,    # include all models
                }
            ],
            'static_url_path': '/flasgger_static',
            'swagger_ui': True,
            'specs_route': '/apidocs'               # serve UI at /apidocs
        }
    )
