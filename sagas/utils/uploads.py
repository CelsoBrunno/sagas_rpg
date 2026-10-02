# ==========================================
# Helpers de upload de imagens
# ==========================================

import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def salvar_imagem(arquivo, prefixo):
    """Salva a imagem enviada em static/uploads e devolve a URL, ou None se não houver arquivo válido."""
    if not arquivo or not arquivo.filename or not allowed_file(arquivo.filename):
        return None
    nome = secure_filename(f"{prefixo}_{uuid.uuid4().hex[:8]}_{arquivo.filename}")
    arquivo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], nome))
    return f"/static/uploads/{nome}"


def remover_imagem(url):
    """Apaga um arquivo de static/uploads a partir da URL salva no banco."""
    if not url or not url.startswith('/static/uploads/'):
        return
    caminho = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(url))
    try:
        os.remove(caminho)
    except OSError:
        pass
