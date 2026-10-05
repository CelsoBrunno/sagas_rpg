# Upload e listagem de imagens

import os

from flask import Blueprint, current_app, jsonify, request

from models import Imagem
from utils.acesso import verificar_login
from utils.uploads import salvar_imagem

bp = Blueprint('imagens', __name__)

@bp.route('/api/upload', methods=['POST'])
def upload_imagem():
    """Endpoint para upload de imagens"""
    if not verificar_login():
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    if not request.files.get('file'):
        return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    entidade_tipo = request.form.get('entidade_tipo')
    entidade_id = request.form.get('entidade_id')
    
    if not entidade_tipo or not entidade_id:
        return jsonify({'success': False, 'message': 'entidade_tipo e entidade_id são obrigatórios'}), 400
    
    path_url = salvar_imagem(file, f"{entidade_tipo}_{entidade_id}")
    if path_url:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(path_url))
        
        dados = {
            'path_url': path_url,
            'alt_text': request.form.get('alt_text', ''),
            'titulo': request.form.get('titulo', ''),
            'descricao': request.form.get('descricao', ''),
            'entidade_tipo': entidade_tipo,
            'entidade_id': entidade_id,
            'file_size': os.path.getsize(filepath),
            'mime_type': file.content_type,
        }
        
        Imagem.criar(dados)
        
        return jsonify({'success': True, 'message': 'Imagem enviada com sucesso!', 'path': path_url})
    
    return jsonify({'success': False, 'message': 'Arquivo inválido'}), 400

@bp.route('/api/imagens/<entidade_tipo>/<int:entidade_id>')
def listar_imagens_entidade(entidade_tipo, entidade_id):
    """Lista imagens de uma entidade"""
    imagens = Imagem.buscar_por_entidade(entidade_tipo, entidade_id)
    return jsonify(imagens)
