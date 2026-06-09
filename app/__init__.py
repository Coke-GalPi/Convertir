from flask import Flask
from app.routes.public import public_bp
from app.routes.error import error_bp, register_error_handlers

# Crear la aplicación Flask
app = Flask(__name__)

# Registrar los blueprints
app.register_blueprint(public_bp)
app.register_blueprint(error_bp)

# Registrar manejadores globales de error (HTTP y excepciones)
register_error_handlers(app)