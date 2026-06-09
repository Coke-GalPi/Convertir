from flask import Blueprint, render_template
from werkzeug.exceptions import HTTPException
import traceback

error_bp = Blueprint('error', __name__)

def register_error_handlers(app):
    """Registra los manejadores de errores en la aplicación."""
    
    def resolve_error_icon(status_code):
        if status_code >= 500:
            return 'server-crash'
        if status_code >= 400:
            return 'shield-ban'
        return 'triangle-alert'
    
    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        """Captura cualquier error HTTP: 400, 401, 403, 404, 405, etc."""
        return render_template(
            'error/error.html',
            status_code=error.code,
            error_title=error.name,
            error_message=error.description,
            error_icon=resolve_error_icon(error.code),
        ), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Captura errores no controlados y responde con una vista consistente."""
        print(f"ERROR: {error}")
        traceback.print_exc()
        return render_template(
            'error/error.html',
            status_code=500,
            error_title='Error interno del servidor',
            error_message='Ocurrio un problema inesperado. Intenta de nuevo en unos minutos.',
            error_icon=resolve_error_icon(500),
        ), 500