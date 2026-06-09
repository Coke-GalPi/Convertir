import io
import base64
from datetime import datetime as dt
from pathlib import Path
import tempfile
import os

from flask import Blueprint, render_template, request, abort
from PIL import Image

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
@public_bp.route('/index')
def index():
    """Renderiza la página de inicio."""
    current_year = dt.now().year
    return render_template('public/index.html', current_year=current_year)

@public_bp.route('/image')
def image():
    """Renderiza la página de entrada de datos."""
    current_year = dt.now().year
    return render_template('public/image.html', current_year=current_year)

@public_bp.route('/docpdf')
def docpdf():
    """Renderiza la página de entrada de datos para documentos y PDF."""
    current_year = dt.now().year
    return render_template('public/docpdf.html', current_year=current_year)

@public_bp.route('/pdfdocx')
def pdfdocx():
    current_year = dt.now().year
    return render_template('public/pdftoword.html', current_year=current_year)

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

@public_bp.route('/mergepdf', methods=['POST'])
def mergepdf():
    """Fusiona los archivos PDF subidos en un solo PDF."""
    files = request.files.getlist('files')
    if not files or any(not f.filename for f in files):
        abort(400, description='Debes seleccionar al menos un archivo PDF.')
    # Validación: comprobar extensión, mimetype y magic bytes PDF
    for f in files:
        filename = f.filename or ''
        if not filename.lower().endswith('.pdf'):
            abort(400, description=f'El archivo "{filename}" no tiene extensión .pdf')
        mimetype = getattr(f, 'mimetype', '') or ''
        if mimetype and 'pdf' not in mimetype.lower():
            abort(400, description=f'El archivo "{filename}" no parece ser un PDF (mimetype incorrecto).')
        # Leer los primeros bytes para verificar la firma PDF
        try:
            start_pos = None
            if hasattr(f.stream, 'tell') and hasattr(f.stream, 'seek'):
                start_pos = f.stream.tell()
            head = f.stream.read(4)
            if start_pos is not None:
                f.stream.seek(start_pos)
        except Exception:
            abort(400, description=f'No se pudo validar el contenido de "{filename}".')
        if not head or not head.startswith(b'%PDF'):
            abort(400, description=f'El archivo "{filename}" no es un PDF válido.')
    from PyPDF2 import PdfMerger
    merger = PdfMerger()
    for file in files:
        merger.append(file.stream)
    output_buffer = io.BytesIO()
    merger.write(output_buffer)
    merger.close()
    output_buffer.seek(0)
    download_name = 'documento_fusionado.pdf'
    encoded_data = base64.b64encode(output_buffer.getvalue()).decode('ascii')
    data_url = f'data:application/pdf;base64,{encoded_data}'
    current_year = dt.now().year
    return render_template(
        'public/output.html',
        current_year=current_year,
        conversion_ready=True,
        output_format='pdf',
        download_name=download_name,
        mimetype='application/pdf',
        preview_data_url=data_url,
        original_name=', '.join(f.filename for f in files),
    )

@public_bp.route('/pdftoword', methods=['POST'])
def pdftoword():
    """Convierte un archivo PDF a formato Word (docx)."""
    file = request.files.get('file')
    if not file or not file.filename:
        abort(400, description='Debes seleccionar un archivo PDF.')
    filename = file.filename
    if not filename.lower().endswith('.pdf'):
        abort(400, description='El archivo seleccionado no tiene extensión .pdf')
    mimetype = getattr(file, 'mimetype', '') or ''
    if mimetype and 'pdf' not in mimetype.lower():
        abort(400, description='El archivo seleccionado no parece ser un PDF (mimetype incorrecto).')
    try:
        start_pos = None
        if hasattr(file.stream, 'tell') and hasattr(file.stream, 'seek'):
            start_pos = file.stream.tell()
        head = file.stream.read(4)
        if start_pos is not None:
            file.stream.seek(start_pos)
    except Exception:
        abort(400, description='No se pudo validar el contenido del archivo.')
    if not head or not head.startswith(b'%PDF'):
        abort(400, description='El archivo seleccionado no es un PDF válido.')
    from pdf2docx import Converter
    # Guardar el PDF subido en un archivo temporal y convertir a docx en otro temporal
    tmp_pdf = None
    tmp_docx = None
    try:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tpdf:
            tmp_pdf = tpdf.name
            file.stream.seek(0)
            tpdf.write(file.stream.read())
            tpdf.flush()
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tdocx:
            tmp_docx = tdocx.name

        try:
            cv = Converter(tmp_pdf)
            cv.convert(tmp_docx)
            cv.close()
        except Exception as e:
            abort(500, description=f'Error al convertir el PDF: {str(e)}')

        with open(tmp_docx, 'rb') as fdoc:
            output_bytes = fdoc.read()

        output_buffer = io.BytesIO(output_bytes)
        output_buffer.seek(0)
        original_name = Path(filename).stem or 'documento_convertido'
        download_name = f'{original_name}.docx'
        encoded_data = base64.b64encode(output_buffer.getvalue()).decode('ascii')
        data_url = f'data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{encoded_data}'
    finally:
        try:
            if tmp_pdf and os.path.exists(tmp_pdf):
                os.remove(tmp_pdf)
        except Exception:
            pass
        try:
            if tmp_docx and os.path.exists(tmp_docx):
                os.remove(tmp_docx)
        except Exception:
            pass
    current_year = dt.now().year
    return render_template(
        'public/output.html',
        current_year=current_year,
        conversion_ready=True,
        output_format='docx',
        download_name=download_name,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        preview_data_url=data_url,
        original_name=filename,
    )