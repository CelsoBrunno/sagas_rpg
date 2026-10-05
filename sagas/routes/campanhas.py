# Campanhas e fichas do jogador

from flask import flash, redirect, render_template, request, session, url_for
from database import Database
from models import Campanha
from flask import Blueprint

bp = Blueprint('campanhas', __name__)
from utils.acesso import pode_gerenciar_personagem, verificar_admin, verificar_login, exigir_login, exigir_admin

@bp.route('/campanhas', methods=['GET', 'POST'])
@exigir_login
def listar_campanhas():
    """Lista as campanhas e permite entrar em uma delas"""

    if request.method == 'POST':
        if not verificar_admin():
            flash('Apenas administradores podem criar campanhas.', 'danger')
            return redirect(url_for('campanhas.listar_campanhas'))
        nome = (request.form.get('nome_campanha') or '').strip()
        if not nome:
            flash('Nome da campanha é obrigatório.', 'danger')
            return redirect(url_for('campanhas.listar_campanhas'))
        try:
            pontos = int(request.form.get('pontos_iniciais') or 150)
        except (TypeError, ValueError):
            pontos = 150
        novo_id = Campanha.criar({
            'nome_campanha': nome,
            'id_mestre': session.get('user_id'),
            'pontos_iniciais': pontos,
            'descricao': request.form.get('descricao'),
            'status': 'Ativa',
        })
        session['campanha_id'] = novo_id
        flash(f'Campanha {nome} criada. Você já está nela.', 'success')
        return redirect(url_for('ficha.index'))
    
    campanhas = Campanha.listar_todas()
    return render_template('campanhas_index.html', campanhas=campanhas)

@bp.route('/campanha/<int:id>/entrar', methods=['POST'])
@exigir_login
def entrar_campanha(id):
    """Define a campanha ativa da sessão"""

    campanha = Campanha.buscar_por_id(id)
    if not campanha:
        flash('Campanha não encontrada.', 'danger')
        return redirect(url_for('campanhas.listar_campanhas'))

    session['campanha_id'] = campanha['id']
    flash(f'Você entrou na campanha {campanha["nome_campanha"]}.', 'success')
    return redirect(url_for('ficha.index'))

@bp.route('/campanha/<int:id>', methods=['GET', 'POST'])
@exigir_login
def ver_campanha(id):
    """Visualiza e atualiza uma campanha"""
    
    campanha = Campanha.buscar_por_id(id)
    if not campanha:
        flash('Campanha não encontrada.', 'danger')
        return redirect(url_for('campanhas.listar_campanhas'))

    if request.method == 'POST':
        if not verificar_admin():
            flash('Apenas administradores podem alterar a campanha.', 'danger')
            return redirect(url_for('campanhas.ver_campanha', id=id))

        if request.form.get('usuario_id'):
            try:
                usuario_id = int(request.form.get('usuario_id'))
            except (TypeError, ValueError):
                flash('ID do jogador inválido.', 'danger')
                return redirect(url_for('campanhas.ver_campanha', id=id))
            Campanha.convidar_jogador(id, usuario_id)
            flash('Jogador convidado para a campanha.', 'success')
            return redirect(url_for('campanhas.ver_campanha', id=id))

        nome = (request.form.get('nome_campanha') or '').strip()
        if not nome:
            flash('Nome da campanha é obrigatório.', 'danger')
            return redirect(url_for('campanhas.ver_campanha', id=id))
        try:
            pontos = int(request.form.get('pontos_iniciais'))
        except (TypeError, ValueError):
            flash('Pontos iniciais inválidos.', 'danger')
            return redirect(url_for('campanhas.ver_campanha', id=id))
        if pontos < 0:
            flash('Pontos iniciais não podem ser negativos.', 'danger')
            return redirect(url_for('campanhas.ver_campanha', id=id))

        tema = request.form.get('tema') or campanha.get('tema') or 'padrao'
        if tema not in Campanha.TEMAS:
            tema = 'padrao'

        Campanha.atualizar(id, {
            'nome_campanha': nome,
            'pontos_iniciais': pontos,
            'descricao': request.form.get('descricao'),
            'status': campanha.get('status') or 'Ativa',
            'tema': tema,
        })
        flash('Campanha atualizada.', 'success')
        return redirect(url_for('campanhas.ver_campanha', id=id))
    
    # Busca personagens da campanha
    query = """
        SELECT p.*, u.username 
        FROM personagens p 
        LEFT JOIN usuarios u ON p.id_usuario_jogador = u.id
        WHERE p.id_campanha = %s
        ORDER BY p.status_criacao, p.nome
    """
    personagens = Database.execute_query(query, (id,)) or []
    if not verificar_admin():
        personagens = [p for p in personagens if pode_gerenciar_personagem(p)]
    
    return render_template('campanha_detalhe.html', campanha=campanha, personagens=personagens,
                           temas=Campanha.TEMAS)

@bp.route('/meus-personagens')
@exigir_login
def meus_personagens():
    """Lista personagens pendentes/em andamento do jogador"""
    
    user_id = session.get('user_id')
    
    query = """
        SELECT p.*, c.nome_campanha, c.pontos_iniciais
        FROM personagens p
        JOIN campanhas c ON p.id_campanha = c.id
        WHERE p.id_usuario_jogador = %s
        AND p.status_criacao IN ('Pendente', 'Em_Andamento')
        ORDER BY p.created_at DESC
    """
    personagens = Database.execute_query(query, (user_id,))
    
    return render_template('meus_personagens.html', personagens=personagens)
