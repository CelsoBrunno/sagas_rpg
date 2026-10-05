# Locais, NPCs, mapas e busca

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from config import Config
from database import Database
from models import Local, Mapa, NPC, Personagem
from utils.acesso import (
    campanha_da_sessao, exigir_admin, exigir_campanha, exigir_login,
    pertence_a_campanha_ativa, verificar_admin, verificar_login,
)
from utils.uploads import allowed_file, remover_imagem, salvar_imagem

bp = Blueprint('mundo', __name__)

@bp.route('/locais')
@exigir_login
def listar_locais():
    """Lista todos os locais"""
    
    campanha = campanha_da_sessao()
    locais = Local.listar_por_campanha(campanha['id']) if campanha else []
    return render_template('locais_index.html', locais=locais, sem_campanha=campanha is None)

@bp.route('/local/<int:id>')
@exigir_login
def ver_local(id):
    """Visualiza detalhes de um local"""

    local = Local.buscar_por_id(id)
    if not local or not pertence_a_campanha_ativa(local):
        flash('Local não encontrado nesta campanha.', 'danger')
        return redirect(url_for('mundo.listar_locais'))
    
    # Debug: verificar imagem
    if Config.DEBUG and local.get('imagem_principal_url'):
        print(f"DEBUG: Local {id} - imagem_principal_url: {local.get('imagem_principal_url')}")
    
    # Busca NPCs presentes neste local
    npcs = NPC.listar_por_local(id) or []

    # Notas de mestre e lore completa ficam fora da página do jogador
    if not verificar_admin():
        local = dict(local)
        local['descricao_mestre'] = None
        npcs_publicos = []
        for npc in npcs:
            npc_publico = dict(npc)
            npc_publico['descricao_completa'] = None
            npcs_publicos.append(npc_publico)
        npcs = npcs_publicos
    
    # Busca mapas associados a este local
    mapas = Mapa.listar_por_local(id)
    
    return render_template('local_detalhe.html',
                         local=local,
                         npcs=npcs,
                         mapas=mapas)

@bp.route('/local/novo', methods=['GET', 'POST'])
@exigir_admin(mensagem='Apenas administradores podem criar locais.', destino='mundo.listar_locais')
def novo_local():
    """Cria um novo local"""

    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('campanhas.listar_campanhas'))
    
    if request.method == 'POST':
        arquivo = request.files.get('arquivo')
        if arquivo and arquivo.filename and not allowed_file(arquivo.filename):
            flash('Tipo de arquivo inválido. Use PNG, JPG, JPEG, GIF ou WEBP.', 'danger')
            return render_template('local_form.html', local=None)
        imagem_url = salvar_imagem(arquivo, 'local')
        
        dados = {
            'nome': request.form.get('nome'),
            'tipo': request.form.get('tipo'),
            'descricao_publica': request.form.get('descricao_publica'),
            'descricao_mestre': request.form.get('descricao_mestre'),
            'imagem_principal_url': imagem_url,
            'id_campanha': campanha['id']
        }
        
        if not dados['nome']:
            flash('Nome é obrigatório.', 'danger')
            return render_template('local_form.html')
        
        try:
            local_id = Local.criar(dados)
            flash('Local criado com sucesso!', 'success')
            return redirect(url_for('mundo.ver_local', id=local_id))
        except Exception as e:
            flash(f'Erro ao criar local: {str(e)}', 'danger')
    
    return render_template('local_form.html')

@bp.route('/local/<int:id>/editar', methods=['GET', 'POST'])
@exigir_admin(mensagem='Apenas administradores podem editar locais.', destino='mundo.listar_locais')
def editar_local(id):
    """Edita um local existente"""
    
    local = Local.buscar_por_id(id)
    if not local or not pertence_a_campanha_ativa(local):
        flash('Local não encontrado nesta campanha.', 'danger')
        return redirect(url_for('mundo.listar_locais'))
    
    if request.method == 'POST':
        imagem_url = local.get('imagem_principal_url')
        arquivo = request.files.get('arquivo')
        if arquivo and arquivo.filename and not allowed_file(arquivo.filename):
            flash('Tipo de arquivo inválido. Use PNG, JPG, JPEG, GIF ou WEBP.', 'danger')
            return render_template('local_form.html', local=local)
        nova = salvar_imagem(arquivo, 'local')
        if nova:
            remover_imagem(imagem_url)
            imagem_url = nova
        
        dados = {
            'nome': request.form.get('nome'),
            'tipo': request.form.get('tipo'),
            'descricao_publica': request.form.get('descricao_publica'),
            'descricao_mestre': request.form.get('descricao_mestre'),
            'imagem_principal_url': imagem_url
        }
        
        if not dados['nome']:
            flash('Nome é obrigatório.', 'danger')
            return render_template('local_form.html', local=local)
        
        try:
            Local.atualizar(id, dados)
            flash('Local atualizado com sucesso!', 'success')
            return redirect(url_for('mundo.ver_local', id=id))
        except Exception as e:
            flash(f'Erro ao atualizar local: {str(e)}', 'danger')
    
    return render_template('local_form.html', local=local)

@bp.route('/local/<int:id>/deletar', methods=['POST'])
@exigir_admin(mensagem='Apenas administradores podem deletar locais.', destino='mundo.listar_locais')
def deletar_local(id):
    """Deleta um local"""
    
    local = Local.buscar_por_id(id)
    if not local or not pertence_a_campanha_ativa(local):
        flash('Local não encontrado nesta campanha.', 'danger')
        return redirect(url_for('mundo.listar_locais'))
    
    try:
        remover_imagem(local.get('imagem_principal_url'))
        Local.deletar(id)
        flash('Local deletado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao deletar local: {str(e)}', 'danger')
    
    return redirect(url_for('mundo.listar_locais'))

# ==========================================
# Rotas - NPCs (Módulo 3)
# ==========================================

@bp.route('/npcs')
@exigir_login
def listar_npcs():
    """Lista todos os NPCs"""
    
    campanha = campanha_da_sessao()
    npcs = NPC.listar_por_campanha(campanha['id']) if campanha else []
    return render_template('npcs_index.html', npcs=npcs, sem_campanha=campanha is None)

@bp.route('/npc/<int:id>')
@exigir_login
def ver_npc(id):
    """Visualiza detalhes de um NPC"""

    npc = NPC.buscar_por_id(id)
    if not npc or not pertence_a_campanha_ativa(npc):
        flash('NPC não encontrado nesta campanha.', 'danger')
        return redirect(url_for('mundo.listar_npcs'))

    if not verificar_admin():
        npc = dict(npc)
        npc['descricao_completa'] = None
    
    return render_template('npc_detalhe.html', npc=npc)

@bp.route('/npc/novo', methods=['GET', 'POST'])
@exigir_admin(mensagem='Apenas administradores podem criar NPCs.', destino='mundo.listar_npcs')
def novo_npc():
    """Cria um novo NPC"""

    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('campanhas.listar_campanhas'))
    
    if request.method == 'POST':
        arquivo = request.files.get('arquivo')
        if arquivo and arquivo.filename and not allowed_file(arquivo.filename):
            flash('Tipo de arquivo inválido. Use PNG, JPG, JPEG, GIF ou WEBP.', 'danger')
            locais = Local.listar_por_campanha(campanha['id'])
            personagens = Personagem.listar_por_campanha(campanha['id'])
            return render_template('npc_form.html', locais=locais, personagens=personagens)
        imagem_url = salvar_imagem(arquivo, 'npc')
        
        dados = {
            'nome': request.form.get('nome'),
            'status': request.form.get('status', 'Vivo'),
            'descricao_breve': request.form.get('descricao_breve'),
            'descricao_completa': request.form.get('descricao_completa'),
            'imagem_url': imagem_url,
            'local_atual_id': request.form.get('local_atual_id') or None,
            'ficha_personagem_id': request.form.get('ficha_personagem_id') or None,
            'id_campanha': campanha['id']
        }
        
        if dados['local_atual_id']:
            dados['local_atual_id'] = int(dados['local_atual_id'])
        if dados['ficha_personagem_id']:
            dados['ficha_personagem_id'] = int(dados['ficha_personagem_id'])
        
        if not dados['nome']:
            flash('Nome é obrigatório.', 'danger')
            locais = Local.listar_por_campanha(campanha['id'])
            personagens = Personagem.listar_por_campanha(campanha['id'])
            return render_template('npc_form.html', locais=locais, personagens=personagens)
        
        try:
            npc_id = NPC.criar(dados)
            flash('NPC criado com sucesso!', 'success')
            return redirect(url_for('mundo.ver_npc', id=npc_id))
        except Exception as e:
            flash(f'Erro ao criar NPC: {str(e)}', 'danger')
    
    locais = Local.listar_por_campanha(campanha['id'])
    personagens = Personagem.listar_por_campanha(campanha['id'])
    return render_template('npc_form.html', locais=locais, personagens=personagens)

@bp.route('/npc/<int:id>/editar', methods=['GET', 'POST'])
@exigir_admin(mensagem='Apenas administradores podem editar NPCs.', destino='mundo.listar_npcs')
def editar_npc(id):
    """Edita um NPC existente"""
    
    npc = NPC.buscar_por_id(id)
    if not npc or not pertence_a_campanha_ativa(npc):
        flash('NPC não encontrado nesta campanha.', 'danger')
        return redirect(url_for('mundo.listar_npcs'))

    campanha = campanha_da_sessao()
    
    if request.method == 'POST':
        imagem_url = npc.get('imagem_url')
        arquivo = request.files.get('arquivo')
        if arquivo and arquivo.filename and not allowed_file(arquivo.filename):
            flash('Tipo de arquivo inválido. Use PNG, JPG, JPEG, GIF ou WEBP.', 'danger')
            locais = Local.listar_por_campanha(session.get('campanha_id'))
            personagens = Personagem.listar_por_campanha(session.get('campanha_id'))
            return render_template('npc_form.html', npc=npc, locais=locais, personagens=personagens)
        nova = salvar_imagem(arquivo, 'npc')
        if nova:
            remover_imagem(imagem_url)
            imagem_url = nova
        
        dados = {
            'nome': request.form.get('nome'),
            'status': request.form.get('status', 'Vivo'),
            'descricao_breve': request.form.get('descricao_breve'),
            'descricao_completa': request.form.get('descricao_completa'),
            'imagem_url': imagem_url,
            'local_atual_id': request.form.get('local_atual_id') or None,
            'ficha_personagem_id': request.form.get('ficha_personagem_id') or None
        }
        
        if dados['local_atual_id']:
            dados['local_atual_id'] = int(dados['local_atual_id'])
        if dados['ficha_personagem_id']:
            dados['ficha_personagem_id'] = int(dados['ficha_personagem_id'])
        
        if not dados['nome']:
            flash('Nome é obrigatório.', 'danger')
            locais = Local.listar_por_campanha(session.get('campanha_id'))
            personagens = Personagem.listar_por_campanha(session.get('campanha_id'))
            return render_template('npc_form.html', npc=npc, locais=locais, personagens=personagens)
        
        try:
            NPC.atualizar(id, dados)
            flash('NPC atualizado com sucesso!', 'success')
            return redirect(url_for('mundo.ver_npc', id=id))
        except Exception as e:
            flash(f'Erro ao atualizar NPC: {str(e)}', 'danger')
    
    locais = Local.listar_por_campanha(session.get('campanha_id'))
    personagens = Personagem.listar_por_campanha(session.get('campanha_id'))
    return render_template('npc_form.html', npc=npc, locais=locais, personagens=personagens)

@bp.route('/npc/<int:id>/deletar', methods=['POST'])
@exigir_admin(mensagem='Apenas administradores podem deletar NPCs.', destino='mundo.listar_npcs')
def deletar_npc(id):
    """Deleta um NPC"""
    
    npc = NPC.buscar_por_id(id)
    if not npc or not pertence_a_campanha_ativa(npc):
        flash('NPC não encontrado nesta campanha.', 'danger')
        return redirect(url_for('mundo.listar_npcs'))
    
    try:
        remover_imagem(npc.get('imagem_url'))
        NPC.deletar(id)
        flash('NPC deletado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao deletar NPC: {str(e)}', 'danger')
    
    return redirect(url_for('mundo.listar_npcs'))

@bp.route('/api/npc/<int:id>/mover', methods=['POST'])
def mover_npc(id):
    """Move um NPC para outro local"""
    if not verificar_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    dados = request.json or {}
    novo_local_id = dados.get('local_id')
    
    if not novo_local_id:
        return jsonify({'success': False, 'message': 'ID do local é obrigatório'}), 400
    
    try:
        NPC.mover_para_local(id, int(novo_local_id))
        return jsonify({'success': True, 'message': 'NPC movido com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==========================================
# Rotas - Mapas (Módulo 4)
# ==========================================

@bp.route('/mapas')
@exigir_login
def listar_mapas():
    """Lista todos os mapas"""
    
    campanha = campanha_da_sessao()
    mapas = Mapa.listar_por_campanha(campanha['id']) if campanha else []
    return render_template('mapas_index.html', mapas=mapas, sem_campanha=campanha is None)

@bp.route('/mapa/<int:id>')
@exigir_login
def ver_mapa(id):
    """Visualiza um mapa"""

    mapa = Mapa.buscar_por_id(id)
    if not mapa or not pertence_a_campanha_ativa(mapa):
        flash('Mapa não encontrado nesta campanha.', 'danger')
        return redirect(url_for('mundo.listar_mapas'))
    
    return render_template('mapa_detalhe.html', mapa=mapa)

@bp.route('/mapa/novo', methods=['GET', 'POST'])
@exigir_admin(mensagem='Apenas administradores podem criar mapas.', destino='mundo.listar_mapas')
def novo_mapa():
    """Cria um novo mapa"""

    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('campanhas.listar_campanhas'))
    
    if request.method == 'POST':
        arquivo = request.files.get('arquivo')
        if not arquivo or not arquivo.filename:
            flash('É necessário fazer upload de uma imagem.', 'danger')
            locais = Local.listar_por_campanha(session.get('campanha_id'))
            return render_template('mapa_form.html', locais=locais)
        if not allowed_file(arquivo.filename):
            flash('Tipo de arquivo inválido. Use PNG, JPG, JPEG, GIF ou WEBP.', 'danger')
            locais = Local.listar_por_campanha(session.get('campanha_id'))
            return render_template('mapa_form.html', locais=locais)
        url_imagem = salvar_imagem(arquivo, 'mapa')
        
        dados = {
            'nome_mapa': request.form.get('nome_mapa'),
            'tipo_mapa': request.form.get('tipo_mapa'),
            'descricao': request.form.get('descricao'),
            'local_associado_id': request.form.get('local_associado_id') or None,
            'url_imagem': url_imagem,
            'id_campanha': campanha['id']
        }
        
        if dados['local_associado_id']:
            dados['local_associado_id'] = int(dados['local_associado_id'])
        
        if not dados['nome_mapa']:
            flash('Nome do mapa é obrigatório.', 'danger')
            locais = Local.listar_por_campanha(session.get('campanha_id'))
            return render_template('mapa_form.html', locais=locais)
        
        try:
            mapa_id = Mapa.criar(dados)
            flash('Mapa criado com sucesso!', 'success')
            return redirect(url_for('mundo.ver_mapa', id=mapa_id))
        except Exception as e:
            flash(f'Erro ao criar mapa: {str(e)}', 'danger')
    
    locais = Local.listar_por_campanha(session.get('campanha_id'))
    return render_template('mapa_form.html', locais=locais)

@bp.route('/mapa/<int:id>/editar', methods=['GET', 'POST'])
@exigir_admin(mensagem='Apenas administradores podem editar mapas.', destino='mundo.listar_mapas')
def editar_mapa(id):
    """Edita um mapa existente"""
    
    mapa = Mapa.buscar_por_id(id)
    if not mapa or not pertence_a_campanha_ativa(mapa):
        flash('Mapa não encontrado nesta campanha.', 'danger')
        return redirect(url_for('mundo.listar_mapas'))
    
    if request.method == 'POST':
        url_imagem = mapa.get('url_imagem')
        arquivo = request.files.get('arquivo')
        if arquivo and arquivo.filename and not allowed_file(arquivo.filename):
            flash('Tipo de arquivo inválido. Use PNG, JPG, JPEG, GIF ou WEBP.', 'danger')
            locais = Local.listar_por_campanha(session.get('campanha_id'))
            return render_template('mapa_form.html', mapa=mapa, locais=locais)
        nova = salvar_imagem(arquivo, 'mapa')
        if nova:
            remover_imagem(url_imagem)
            url_imagem = nova
        
        dados = {
            'nome_mapa': request.form.get('nome_mapa'),
            'tipo_mapa': request.form.get('tipo_mapa'),
            'descricao': request.form.get('descricao'),
            'local_associado_id': request.form.get('local_associado_id') or None,
            'url_imagem': url_imagem
        }
        
        if dados['local_associado_id']:
            dados['local_associado_id'] = int(dados['local_associado_id'])
        
        if not dados['nome_mapa']:
            flash('Nome do mapa é obrigatório.', 'danger')
            locais = Local.listar_por_campanha(session.get('campanha_id'))
            return render_template('mapa_form.html', mapa=mapa, locais=locais)
        
        try:
            Mapa.atualizar(id, dados)
            flash('Mapa atualizado com sucesso!', 'success')
            return redirect(url_for('mundo.ver_mapa', id=id))
        except Exception as e:
            flash(f'Erro ao atualizar mapa: {str(e)}', 'danger')
    
    locais = Local.listar_por_campanha(session.get('campanha_id'))
    return render_template('mapa_form.html', mapa=mapa, locais=locais)

@bp.route('/mapa/<int:id>/deletar', methods=['POST'])
@exigir_admin(mensagem='Apenas administradores podem deletar mapas.', destino='mundo.listar_mapas')
def deletar_mapa(id):
    """Deleta um mapa"""
    
    mapa = Mapa.buscar_por_id(id)
    if not mapa or not pertence_a_campanha_ativa(mapa):
        flash('Mapa não encontrado nesta campanha.', 'danger')
        return redirect(url_for('mundo.listar_mapas'))
    
    try:
        remover_imagem(mapa.get('url_imagem'))
        Mapa.deletar(id)
        flash('Mapa deletado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao deletar mapa: {str(e)}', 'danger')
    
    return redirect(url_for('mundo.listar_mapas'))

# ==========================================
# APIs - Busca Global
# ==========================================

@bp.route('/api/busca')
def busca_global():
    """Busca global em todos os módulos"""
    if not verificar_login():
        return jsonify({'results': [], 'erro': 'login necessário'}), 401

    termo = request.args.get('q', '')
    
    if not termo:
        return jsonify({'results': []})

    campanha = campanha_da_sessao()
    if not campanha:
        return jsonify({'results': []})
    campanha_id = campanha['id']
    
    resultados = []
    
    # Busca em locais
    locais = Local.buscar(termo, campanha_id)
    for local in locais:
        resultados.append({
            'tipo': 'local',
            'id': local['id'],
            'nome': local['nome'],
            'descricao': local.get('descricao_publica', '')[:100]
        })
    
    # Busca em NPCs
    npcs = NPC.buscar(termo, campanha_id)
    for npc in npcs:
        resultados.append({
            'tipo': 'npc',
            'id': npc['id'],
            'nome': npc['nome'],
            'descricao': npc.get('descricao_breve', '')[:100]
        })
    
    # Busca em mapas
    mapas = Mapa.buscar(termo, campanha_id)
    for mapa in mapas:
        resultados.append({
            'tipo': 'mapa',
            'id': mapa['id'],
            'nome': mapa['nome_mapa'],
            'descricao': mapa.get('descricao', '')[:100]
        })
    
    # Busca em personagens
    query_personagens = "SELECT * FROM personagens WHERE nome LIKE %s AND id_campanha = %s"
    termo_like = f"%{termo}%"
    personagens = Database.execute_query(query_personagens, (termo_like, campanha_id))
    for personagem in personagens:
        resultados.append({
            'tipo': 'personagem',
            'id': personagem['id'],
            'nome': personagem['nome'],
            'descricao': personagem.get('biografia', '')[:100] if personagem.get('biografia') else ''
        })
    
    return jsonify({'results': resultados})
