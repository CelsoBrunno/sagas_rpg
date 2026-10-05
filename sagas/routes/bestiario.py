# ==========================================
# Rotas do Bestiário
# Jogadores veem cards pretos até o mestre marcar a criatura como
# avistada (foto) ou derrotada (ficha completa).
# ==========================================

from flask import Blueprint, render_template, request, redirect, url_for, flash

from models import Bestiario, Personagem
from utils.acesso import verificar_login, verificar_admin, exigir_campanha, pertence_a_campanha_ativa, exigir_login, exigir_admin
from utils.uploads import salvar_imagem, remover_imagem

bp = Blueprint('bestiario', __name__, url_prefix='/bestiario')


def _fichas_npc(campanha_id):
    return [p for p in (Personagem.listar_por_campanha(campanha_id) or []) if p.get('tipo') == 'NPC']


def _dados_do_formulario(criatura=None):
    ficha_id = request.form.get('ficha_personagem_id')
    imagem_url = salvar_imagem(request.files.get('arquivo'), 'bestiario')
    if imagem_url and criatura:
        remover_imagem(criatura.get('imagem_url'))
    return {
        'nome': (request.form.get('nome') or '').strip(),
        'categoria': (request.form.get('categoria') or '').strip() or None,
        'descricao_publica': request.form.get('descricao_publica'),
        'descricao_mestre': request.form.get('descricao_mestre'),
        'imagem_url': imagem_url or (criatura or {}).get('imagem_url'),
        'ficha_personagem_id': int(ficha_id) if ficha_id else None,
        'nivel_revelacao': Bestiario.nivel_valido(request.form.get('nivel_revelacao')),
    }


def _visao_do_jogador(criatura):
    """Avistada mostra só foto e nome; a ficha completa vem ao derrotar."""
    ocultos = {'descricao_mestre'}
    if criatura['nivel_revelacao'] < Bestiario.DERROTADA:
        ocultos |= {'descricao_publica', 'ficha_personagem_id', 'categoria'}
    return {k: v for k, v in criatura.items() if k not in ocultos}


def _salvar_galeria(criatura_id):
    for arquivo in request.files.getlist('galeria'):
        imagem_url = salvar_imagem(arquivo, 'bestiario')
        if imagem_url:
            Bestiario.adicionar_imagem(criatura_id, imagem_url)


def _criatura_da_campanha(criatura_id):
    criatura = Bestiario.buscar_por_id(criatura_id)
    if not criatura or not pertence_a_campanha_ativa(criatura):
        flash('Criatura não encontrada nesta campanha.', 'danger')
        return None
    return criatura


@bp.route('/')
@exigir_login
def listar_bestiario():
    campanha = exigir_campanha()
    criaturas = Bestiario.listar_por_campanha(campanha['id']) if campanha else []
    if not verificar_admin():
        criaturas = [_visao_do_jogador(c) for c in criaturas]
    return render_template('bestiario_index.html', criaturas=criaturas, sem_campanha=campanha is None,
                           niveis=Bestiario.NIVEIS)


@bp.route('/<int:id>')
@exigir_login
def ver_criatura(id):
    criatura = _criatura_da_campanha(id)
    e_mestre = verificar_admin()
    if not criatura or (criatura['nivel_revelacao'] == Bestiario.OCULTA and not e_mestre):
        if criatura:
            flash('Esta criatura ainda não foi revelada.', 'info')
        return redirect(url_for('bestiario.listar_bestiario'))
    if not e_mestre:
        criatura = _visao_do_jogador(criatura)
    return render_template('bestiario_detalhe.html', criatura=criatura, niveis=Bestiario.NIVEIS,
                           imagens=Bestiario.listar_imagens(id))


@bp.route('/nova', methods=['GET', 'POST'])
@exigir_admin(mensagem='Apenas o mestre pode cadastrar criaturas.', destino='bestiario.listar_bestiario')
def nova_criatura():
    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('campanhas.listar_campanhas'))

    if request.method == 'POST':
        dados = _dados_do_formulario()
        if not dados['nome']:
            flash('Nome da criatura é obrigatório.', 'danger')
            return redirect(url_for('bestiario.nova_criatura'))
        dados['id_campanha'] = campanha['id']
        try:
            novo_id = Bestiario.criar(dados)
        except Exception:
            remover_imagem(dados['imagem_url'])
            flash('Já existe uma criatura com esse nome nesta campanha.', 'danger')
            return redirect(url_for('bestiario.nova_criatura'))
        _salvar_galeria(novo_id)
        flash(f'{dados["nome"]} adicionada ao bestiário.', 'success')
        return redirect(url_for('bestiario.ver_criatura', id=novo_id))

    return render_template('bestiario_form.html', criatura=None, fichas=_fichas_npc(campanha['id']),
                           niveis=Bestiario.NIVEIS)


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@exigir_admin(mensagem='Apenas o mestre pode editar criaturas.', destino='bestiario.listar_bestiario')
def editar_criatura(id):
    criatura = _criatura_da_campanha(id)
    if not criatura:
        return redirect(url_for('bestiario.listar_bestiario'))

    if request.method == 'POST':
        dados = _dados_do_formulario(criatura)
        if not dados['nome']:
            flash('Nome da criatura é obrigatório.', 'danger')
            return redirect(url_for('bestiario.editar_criatura', id=id))
        Bestiario.atualizar(id, dados)
        _salvar_galeria(id)
        flash('Criatura atualizada.', 'success')
        return redirect(url_for('bestiario.ver_criatura', id=id))

    return render_template('bestiario_form.html', criatura=criatura,
                           fichas=_fichas_npc(criatura['id_campanha']), niveis=Bestiario.NIVEIS,
                           imagens=Bestiario.listar_imagens(id))


@bp.route('/<int:id>/imagens/<int:imagem_id>/remover', methods=['POST'])
@exigir_admin(mensagem='Apenas o mestre pode remover imagens.', destino='bestiario.listar_bestiario')
def remover_imagem_galeria(id, imagem_id):
    criatura = _criatura_da_campanha(id)
    imagem = Bestiario.buscar_imagem(imagem_id)
    if criatura and imagem and imagem['id_bestiario'] == id:
        Bestiario.deletar_imagem(imagem_id)
        remover_imagem(imagem['imagem_url'])
        flash('Imagem removida.', 'success')
    return redirect(url_for('bestiario.editar_criatura', id=id))


@bp.route('/<int:id>/revelacao', methods=['POST'])
@exigir_admin(mensagem='Apenas o mestre pode revelar criaturas.', destino='bestiario.listar_bestiario')
def definir_revelacao(id):
    criatura = _criatura_da_campanha(id)
    if criatura:
        nivel = Bestiario.nivel_valido(request.form.get('nivel'))
        Bestiario.definir_revelacao(id, nivel)
        flash(f'{criatura["nome"]}: {Bestiario.NIVEIS[nivel].lower()}.', 'success')
    return redirect(request.referrer or url_for('bestiario.listar_bestiario'))


@bp.route('/<int:id>/deletar', methods=['POST'])
@exigir_admin(mensagem='Apenas o mestre pode remover criaturas.', destino='bestiario.listar_bestiario')
def deletar_criatura(id):
    criatura = _criatura_da_campanha(id)
    if criatura:
        galeria = Bestiario.listar_imagens(id)
        Bestiario.deletar(id)
        for url in [criatura.get('imagem_url')] + [img['imagem_url'] for img in galeria]:
            remover_imagem(url)
        flash(f'{criatura["nome"]} removida do bestiário.', 'success')
    return redirect(url_for('bestiario.listar_bestiario'))
