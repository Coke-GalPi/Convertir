import io
import base64
from datetime import datetime as dt
from pathlib import Path

from flask import Blueprint, render_template, request, abort
from PIL import Image

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
@public_bp.route('/index')
def index():
    """Renderiza la página de entrada de datos."""
    current_year = dt.now().year
    return render_template('public/input.html', current_year=current_year)

@public_bp.route('/convert', methods=['POST'])
def convert():
    """Convierte el archivo subido al formato seleccionado."""
    file = request.files.get('file')
    output_format = (request.form.get('output_format') or request.form.get('description') or '').lower().strip()
    if not file or not file.filename:
        abort(400, description='Debes seleccionar una imagen.')
    if output_format not in {'webp', 'png', 'jpg', 'jpeg', 'gif', 'ico', 'pdf'}:
        abort(400, description='Debes seleccionar un formato de salida válido.')
    source_image = Image.open(file.stream)
    if output_format in {'jpg', 'jpeg', 'pdf'} and source_image.mode in {'RGBA', 'LA', 'P'}:
        source_image = source_image.convert('RGB')
    output_buffer = io.BytesIO()
    save_format = 'JPEG' if output_format in {'jpg', 'jpeg'} else output_format.upper()
    save_kwargs = {}
    if output_format == 'ico':
        save_kwargs['sizes'] = [(256, 256)]
    source_image.save(output_buffer, format=save_format, **save_kwargs)
    output_buffer.seek(0)
    original_name = Path(file.filename).stem or 'imagen_convertida'
    download_name = f'{original_name}.{"jpg" if output_format == "jpeg" else output_format}'
    mimetype_map = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'webp': 'image/webp',
        'gif': 'image/gif',
        'ico': 'image/x-icon',
        'pdf': 'application/pdf',
    }
    encoded_data = base64.b64encode(output_buffer.getvalue()).decode('ascii')
    data_url = f'data:{mimetype_map[output_format]};base64,{encoded_data}'
    current_year = dt.now().year
    return render_template(
        'public/output.html',
        current_year=current_year,
        conversion_ready=True,
        output_format=output_format,
        download_name=download_name,
        mimetype=mimetype_map[output_format],
        preview_data_url=data_url,
        original_name=file.filename,
    )