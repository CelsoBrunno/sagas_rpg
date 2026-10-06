# Admin: sessões, catálogos, usuários, campanhas e fichas

from flask import flash, jsonify, redirect, render_template, request, url_for
import os
from database import Database
from models import Campanha, ItemCatalogo, PericiaCatalogo, Personagem, SessaoLog, Usuario, VantagemDesvantagemCatalogo
from routes.admin import bp
from utils.acesso import campanha_da_sessao, verificar_admin, exigir_login, exigir_admin

@bp.route('/admin/sessoes')
@exigir_admin
def admin_sessoes_form():
    pcs = Database.execute_query("SELECT id, nome FROM personagens WHERE is_pc = TRUE ORDER BY nome")
    return render_template('admin_sessoes_distribuir.html', pcs=pcs)

@bp.route('/admin/sessoes/historico')
@exigir_admin
def admin_sessoes_historico():
    linhas = SessaoLog.listar_historico_sessoes()
    # Agrupa por sessão para renderização simples
    sessoes = {}
    for l in linhas:
        sid = l['id']
        if sid not in sessoes:
            sessoes[sid] = {
                'id': sid,
                'data_sessao': l['data_sessao'],
                'descricao': l['descricao'],
                'itens': []
            }
        if l.get('personagem_id'):
            sessoes[sid]['itens'].append({
                'personagem_nome': l.get('personagem_nome'),
                'pontos_ganhos': l.get('pontos_ganhos')
            })
    return render_template('admin_sessoes_historico.html', sessoes=list(sessoes.values()))

@bp.route('/api/admin/sessoes/distribuir', methods=['POST'])
def api_distribuir_pontos_sessao():
    if not verificar_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    dados = request.json or {}
    try:
        data_sessao = dados['data_sessao']
        descricao = dados.get('descricao', '')
        distribuicoes = dados.get('distribuicoes', [])
        # valida formato
        dist_validas = [
            { 'personagem_id': int(d['personagem_id']), 'pontos': int(d.get('pontos', 0)) }
            for d in distribuicoes if int(d.get('pontos', 0)) != 0
        ]
        if len(dist_validas) == 0:
            return jsonify({'success': False, 'message': 'Nenhum ponto a distribuir'}), 400
        sessao_id = SessaoLog.criar_transacional(data_sessao, descricao, dist_validas)
        return jsonify({'success': True, 'sessao_id': sessao_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==========================================
# Admin - Dashboard
# ==========================================

@bp.route('/admin')
@exigir_admin
def admin_dashboard():
    """Dashboard administrativo. Personagens e pendentes contam só a campanha ativa."""
    campanha = campanha_da_sessao()
    total_personagens = personagens_pendentes = None
    if campanha:
        total_personagens = len(Personagem.listar_por_campanha(campanha['id']) or [])
        personagens_pendentes = len(_da_campanha(Personagem.listar_por_status_criacao('Pendente'), campanha['id']))

    return render_template('admin_dashboard.html',
                         campanha=campanha,
                         total_personagens=total_personagens,
                         personagens_pendentes=personagens_pendentes,
                         total_usuarios=len(Usuario.listar_todos()),
                         total_campanhas=len(Campanha.listar_todas()))


def _da_campanha(personagens, campanha_id):
    return [p for p in (personagens or []) if p.get('id_campanha') == campanha_id]

# ==========================================
# Admin - Gerenciamento de Catálogo de Itens
# ==========================================

@bp.route('/admin/itens')
@exigir_admin
def admin_itens_lista():
    """Lista todos os itens do catálogo"""
    
    return redirect(url_for('admin.admin_catalogo', aba='itens'))

@bp.route('/admin/itens/novo', methods=['GET', 'POST'])
@exigir_admin(mensagem='Acesso restrito ao Mestre (admin).', destino='admin.admin_itens_lista')
def admin_itens_novo():
    """Cria um novo item no catálogo"""
    
    if request.method == 'POST':
        try:
            item_id = ItemCatalogo.criar(
                nome=request.form.get('nome'),
                categoria=request.form.get('categoria', ''),
                preco=float(request.form.get('preco', 0)),
                peso=float(request.form.get('peso', 0)),
                descricao=request.form.get('descricao', ''),
                tipo_item=request.form.get('tipo_item', 'outro'),
                dano_bal_mod=int(request.form.get('dano_bal_mod', 0)) if request.form.get('dano_bal_mod') else None,
                dano_bal_tipo=request.form.get('dano_bal_tipo', '') or None,
                dano_gdp_mod=int(request.form.get('dano_gdp_mod', 0)) if request.form.get('dano_gdp_mod') else None,
                dano_gdp_tipo=request.form.get('dano_gdp_tipo', '') or None,
                rd_mod=int(request.form.get('rd_mod', 0)) if request.form.get('rd_mod') else None,
                rd_tipo=request.form.get('rd_tipo', '') or None
            )
            flash('Item criado com sucesso!', 'success')
            return redirect(url_for('admin.admin_itens_editar', id=item_id))
        except Exception as e:
            flash(f'Erro ao criar item: {str(e)}', 'danger')
    
    return render_template('admin_itens_form.html', item=None)

@bp.route('/admin/itens/<int:id>/editar', methods=['GET', 'POST'])
@exigir_admin(mensagem='Acesso restrito ao Mestre (admin).', destino='admin.admin_itens_lista')
def admin_itens_editar(id):
    """Edita um item do catálogo"""
    
    item = ItemCatalogo.buscar_por_id(id)
    if not item:
        flash('Item não encontrado.', 'danger')
        return redirect(url_for('admin.admin_itens_lista'))
    
    if request.method == 'POST':
        try:
            ItemCatalogo.atualizar(
                item_id=id,
                nome=request.form.get('nome'),
                categoria=request.form.get('categoria'),
                preco=float(request.form.get('preco', 0)) if request.form.get('preco') else None,
                peso=float(request.form.get('peso', 0)) if request.form.get('peso') else None,
                descricao=request.form.get('descricao'),
                tipo_item=request.form.get('tipo_item'),
                dano_bal_mod=int(request.form.get('dano_bal_mod', 0)) if request.form.get('dano_bal_mod') else None,
                dano_bal_tipo=request.form.get('dano_bal_tipo', '') or None,
                dano_gdp_mod=int(request.form.get('dano_gdp_mod', 0)) if request.form.get('dano_gdp_mod') else None,
                dano_gdp_tipo=request.form.get('dano_gdp_tipo', '') or None,
                rd_mod=int(request.form.get('rd_mod', 0)) if request.form.get('rd_mod') else None,
                rd_tipo=request.form.get('rd_tipo', '') or None
            )
            flash('Item atualizado com sucesso!', 'success')
            return redirect(url_for('admin.admin_itens_editar', id=id))
        except Exception as e:
            flash(f'Erro ao atualizar item: {str(e)}', 'danger')
    
    return render_template('admin_itens_form.html', item=item)

@bp.route('/admin/itens/<int:id>/deletar', methods=['POST'])
def admin_itens_deletar(id):
    """Deleta um item do catálogo"""
    if not verificar_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        ItemCatalogo.deletar(id)
        flash('Item deletado com sucesso!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# ==========================================
# Admin - Gerenciamento de Catálogo de Perícias
# ==========================================

@bp.route('/admin/pericias')
@exigir_admin
def admin_pericias_lista():
    """Lista todas as perícias do catálogo"""
    
    return redirect(url_for('admin.admin_catalogo', aba='pericias'))

@bp.route('/admin/pericias/novo', methods=['GET', 'POST'])
@exigir_admin(mensagem='Acesso restrito ao Mestre (admin).', destino='admin.admin_pericias_lista')
def admin_pericias_novo():
    """Cria uma nova perícia no catálogo"""
    
    if request.method == 'POST':
        try:
            pericia_id = PericiaCatalogo.criar(
                nome=request.form.get('nome'),
                atributo_base=request.form.get('atributo_base'),
                dificuldade=request.form.get('dificuldade'),
                custo_texto=request.form.get('custo_texto', ''),
                descricao=request.form.get('descricao', '')
            )
            flash('Perícia criada com sucesso!', 'success')
            return redirect(url_for('admin.admin_pericias_editar', id=pericia_id))
        except Exception as e:
            flash(f'Erro ao criar perícia: {str(e)}', 'danger')
    
    return render_template('admin_pericias_form.html', pericia=None)

@bp.route('/admin/pericias/<int:id>/editar', methods=['GET', 'POST'])
@exigir_admin(mensagem='Acesso restrito ao Mestre (admin).', destino='admin.admin_pericias_lista')
def admin_pericias_editar(id):
    """Edita uma perícia do catálogo"""
    
    pericia = PericiaCatalogo.buscar_por_id(id)
    if not pericia:
        flash('Perícia não encontrada.', 'danger')
        return redirect(url_for('admin.admin_pericias_lista'))
    
    if request.method == 'POST':
        try:
            PericiaCatalogo.atualizar(
                pericia_id=id,
                nome=request.form.get('nome'),
                atributo_base=request.form.get('atributo_base'),
                dificuldade=request.form.get('dificuldade'),
                custo_texto=request.form.get('custo_texto'),
                descricao=request.form.get('descricao')
            )
            flash('Perícia atualizada com sucesso!', 'success')
            return redirect(url_for('admin.admin_pericias_editar', id=id))
        except Exception as e:
            flash(f'Erro ao atualizar perícia: {str(e)}', 'danger')
    
    return render_template('admin_pericias_form.html', pericia=pericia)

@bp.route('/admin/pericias/<int:id>/deletar', methods=['POST'])
def admin_pericias_deletar(id):
    """Deleta uma perícia do catálogo"""
    if not verificar_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        PericiaCatalogo.deletar(id)
        flash('Perícia deletada com sucesso!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# ==========================================
# Admin - Gerenciamento de Catálogo de Vantagens/Desvantagens
# ==========================================

@bp.route('/admin/vantagens')
@exigir_admin
def admin_vantagens_lista():
    """Lista todas as vantagens/desvantagens do catálogo"""
    
    return redirect(url_for('admin.admin_catalogo', aba='vantagens'))

@bp.route('/admin/vantagens/novo', methods=['GET', 'POST'])
@exigir_admin(mensagem='Acesso restrito ao Mestre (admin).', destino='admin.admin_vantagens_lista')
def admin_vantagens_novo():
    """Cria uma nova vantagem/desvantagem no catálogo"""
    
    if request.method == 'POST':
        try:
            vd_id = VantagemDesvantagemCatalogo.criar(
                nome=request.form.get('nome'),
                tipo=request.form.get('tipo'),
                custo_base=int(request.form.get('custo_base', 0)),
                custo_texto=request.form.get('custo_texto', ''),
                descricao=request.form.get('descricao', ''),
                categoria=request.form.get('categoria', '')
            )
            flash('Vantagem/Desvantagem criada com sucesso!', 'success')
            return redirect(url_for('admin.admin_vantagens_editar', id=vd_id))
        except Exception as e:
            flash(f'Erro ao criar vantagem/desvantagem: {str(e)}', 'danger')
    
    return render_template('admin_vantagens_form.html', vantagem=None)

@bp.route('/admin/vantagens/<int:id>/editar', methods=['GET', 'POST'])
@exigir_admin(mensagem='Acesso restrito ao Mestre (admin).', destino='admin.admin_vantagens_lista')
def admin_vantagens_editar(id):
    """Edita uma vantagem/desvantagem do catálogo"""
    
    vantagem = VantagemDesvantagemCatalogo.buscar_por_id(id)
    if not vantagem:
        flash('Vantagem/Desvantagem não encontrada.', 'danger')
        return redirect(url_for('admin.admin_vantagens_lista'))
    
    if request.method == 'POST':
        try:
            VantagemDesvantagemCatalogo.atualizar(
                vd_id=id,
                nome=request.form.get('nome'),
                tipo=request.form.get('tipo'),
                custo_base=int(request.form.get('custo_base', 0)) if request.form.get('custo_base') else None,
                custo_texto=request.form.get('custo_texto'),
                descricao=request.form.get('descricao'),
                categoria=request.form.get('categoria')
            )
            flash('Vantagem/Desvantagem atualizada com sucesso!', 'success')
            return redirect(url_for('admin.admin_vantagens_editar', id=id))
        except Exception as e:
            flash(f'Erro ao atualizar vantagem/desvantagem: {str(e)}', 'danger')
    
    return render_template('admin_vantagens_form.html', vantagem=vantagem)

@bp.route('/admin/vantagens/<int:id>/deletar', methods=['POST'])
def admin_vantagens_deletar(id):
    """Deleta uma vantagem/desvantagem do catálogo"""
    if not verificar_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        VantagemDesvantagemCatalogo.deletar(id)
        flash('Vantagem/Desvantagem deletada com sucesso!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# ==========================================
# Admin - Gerenciamento de Usuários
# ==========================================

@bp.route('/admin/usuarios')
@exigir_admin
def admin_usuarios_lista():
    """Lista todos os usuários"""
    
    usuarios = Usuario.listar_todos()
    return render_template('admin_usuarios_lista.html', usuarios=usuarios)

@bp.route('/admin/usuarios/<int:id>/pontos', methods=['GET', 'POST'])
@exigir_admin
def admin_usuarios_pontos(id):
    """Gerencia pontos de um usuário"""
    
    usuario = Usuario.buscar_por_id(id)
    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('admin.admin_usuarios_lista'))
    
    if request.method == 'POST':
        try:
            acao = request.form.get('acao')
            quantidade = int(request.form.get('quantidade', 0))
            observacao = request.form.get('observacao', '')
            
            if acao == 'adicionar':
                Usuario.adicionar_pontos(id, quantidade)
                flash(f'Adicionados {quantidade} pontos ao usuário {usuario["username"]}.', 'success')
            elif acao == 'remover':
                Usuario.remover_pontos(id, quantidade)
                flash(f'Removidos {quantidade} pontos do usuário {usuario["username"]}.', 'success')
            elif acao == 'definir':
                Usuario.definir_pontos(id, quantidade)
                flash(f'Pontos do usuário {usuario["username"]} definidos para {quantidade}.', 'success')
            else:
                flash('Ação inválida.', 'danger')
            
            # Atualiza dados do usuário
            usuario = Usuario.buscar_por_id(id)
            return redirect(url_for('admin.admin_usuarios_pontos', id=id))
        except Exception as e:
            flash(f'Erro ao gerenciar pontos: {str(e)}', 'danger')
    
    # Busca histórico de alterações (opcional - pode ser implementado depois)
    pontos_atual = Usuario.get_pontos_disponiveis(id)
    
    return render_template('admin_usuarios_pontos.html', usuario=usuario, pontos_atual=pontos_atual)

@bp.route('/admin/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@exigir_admin(mensagem='Acesso restrito ao Mestre (admin).', destino='admin.admin_usuarios_lista')
def admin_usuarios_editar(id):
    """Edita um usuário"""
    
    usuario = Usuario.buscar_por_id(id)
    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('admin.admin_usuarios_lista'))
    
    if request.method == 'POST':
        try:
            Usuario.atualizar(
                user_id=id,
                dados={
                    'role': request.form.get('role'),
                    'is_active': request.form.get('is_active') == '1',
                    'nome_completo': request.form.get('nome_completo'),
                    'email': request.form.get('email')
                }
            )
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('admin.admin_usuarios_editar', id=id))
        except Exception as e:
            flash(f'Erro ao atualizar usuário: {str(e)}', 'danger')
    
    return render_template('admin_usuarios_form.html', usuario=usuario)

# ==========================================
# Admin - Gerenciamento de Campanhas
# ==========================================

@bp.route('/admin/campanhas')
@exigir_admin
def admin_campanhas_lista():
    """Lista todas as campanhas"""
    
    campanhas = Campanha.listar_todas()
    usuarios = Usuario.listar_todos()
    return render_template('admin_campanhas_lista.html', campanhas=campanhas, usuarios=usuarios)

@bp.route('/admin/campanhas/novo', methods=['GET', 'POST'])
@exigir_admin(mensagem='Acesso restrito ao Mestre (admin).', destino='admin.admin_campanhas_lista')
def admin_campanhas_novo():
    """Cria uma nova campanha"""
    
    usuarios = Usuario.listar_todos()
    
    if request.method == 'POST':
        try:
            Campanha.criar({
                'nome_campanha': request.form.get('nome_campanha'),
                'id_mestre': int(request.form.get('id_mestre')),
                'pontos_iniciais': int(request.form.get('pontos_iniciais', 100)),
                'descricao': request.form.get('descricao', ''),
                'status': request.form.get('status', 'Ativa')
            })
            flash('Campanha criada com sucesso!', 'success')
            return redirect(url_for('admin.admin_campanhas_lista'))
        except Exception as e:
            flash(f'Erro ao criar campanha: {str(e)}', 'danger')
    
    return render_template('admin_campanhas_form.html', campanha=None, usuarios=usuarios)

@bp.route('/admin/campanhas/<int:id>/editar', methods=['GET', 'POST'])
@exigir_admin(mensagem='Acesso restrito ao Mestre (admin).', destino='admin.admin_campanhas_lista')
def admin_campanhas_editar(id):
    """Edita uma campanha"""
    
    campanha = Campanha.buscar_por_id(id)
    if not campanha:
        flash('Campanha não encontrada.', 'danger')
        return redirect(url_for('admin.admin_campanhas_lista'))
    
    usuarios = Usuario.listar_todos()
    
    if request.method == 'POST':
        try:
            Campanha.atualizar(id, {
                'nome_campanha': request.form.get('nome_campanha'),
                'pontos_iniciais': int(request.form.get('pontos_iniciais', 100)),
                'descricao': request.form.get('descricao', ''),
                'status': request.form.get('status', 'Ativa')
            })
            flash('Campanha atualizada com sucesso!', 'success')
            return redirect(url_for('admin.admin_campanhas_editar', id=id))
        except Exception as e:
            flash(f'Erro ao atualizar campanha: {str(e)}', 'danger')
    
    return render_template('admin_campanhas_form.html', campanha=campanha, usuarios=usuarios)

# ==========================================
# Admin - Aprovar/Rejeitar Fichas de Personagem
# ==========================================

@bp.route('/admin/personagens')
@exigir_admin
def admin_personagens_lista():
    """Lista todos os personagens (admin)"""
    
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'pendente':
        personagens = Personagem.listar_por_status_criacao('Pendente')
    elif status_filter == 'aprovado':
        personagens = Personagem.listar_por_status_criacao('Aprovado')
    elif status_filter == 'rejeitado':
        personagens = Personagem.listar_por_status_criacao('Rejeitado')
    else:
        personagens = Personagem.listar_todos_admin()

    campanha_filtro = Campanha.buscar_por_id(request.args.get('campanha', type=int) or 0)
    if campanha_filtro:
        personagens = _da_campanha(personagens, campanha_filtro['id'])

    return render_template('admin_personagens_lista.html', personagens=personagens, status_filter=status_filter,
                           campanha_filtro=campanha_filtro)

@bp.route('/admin/personagens/<int:id>/aprovar', methods=['POST'])
def admin_personagens_aprovar(id):
    """Aprova uma ficha de personagem"""
    if not verificar_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        observacoes = request.json.get('observacoes', '') if request.is_json else request.form.get('observacoes', '')
        Personagem.atualizar_status_criacao(id, 'Aprovado', observacoes)
        flash('Ficha aprovada com sucesso!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@bp.route('/admin/personagens/<int:id>/rejeitar', methods=['POST'])
def admin_personagens_rejeitar(id):
    """Rejeita uma ficha de personagem"""
    if not verificar_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        observacoes = request.json.get('observacoes', '') if request.is_json else request.form.get('observacoes', '')
        Personagem.atualizar_status_criacao(id, 'Rejeitado', observacoes)
        flash('Ficha rejeitada.', 'warning')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400
