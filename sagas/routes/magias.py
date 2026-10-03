# ==========================================
# Rotas do Grimório (magias do personagem)
# Os jogadores só veem; quem cadastra e edita é o mestre.
# ==========================================

from flask import Blueprint, request, redirect, url_for, flash

from models import Magia, Personagem
from utils.acesso import verificar_admin, pertence_a_campanha_ativa

bp = Blueprint('magias', __name__)


def _voltar_para_ficha(personagem_id):
    return redirect(url_for('ver_personagem', id=personagem_id) + '#magias')


def _dados_do_formulario():
    def texto(campo):
        return (request.form.get(campo) or '').strip() or None

    nh = texto('nh')
    return {
        'nome': texto('nome'),
        'escola': texto('escola'),
        'nh': int(nh) if nh and nh.lstrip('-').isdigit() else None,
        'custo': texto('custo'),
        'tempo': texto('tempo'),
        'duracao': texto('duracao'),
        'notas': texto('notas'),
    }


def _personagem_editavel(personagem_id):
    """Personagem da campanha ativa, e só para o mestre."""
    if not verificar_admin():
        flash('Apenas o mestre pode alterar o grimório.', 'danger')
        return None
    personagem = Personagem.buscar_por_id(personagem_id)
    if not personagem or (personagem.get('id_campanha') and not pertence_a_campanha_ativa(personagem)):
        flash('Personagem não encontrado nesta campanha.', 'danger')
        return None
    return personagem


def _magia_editavel(magia_id):
    magia = Magia.buscar_por_id(magia_id)
    if not magia:
        flash('Magia não encontrada.', 'danger')
        return None
    return magia if _personagem_editavel(magia['personagem_id']) else None


@bp.route('/personagem/<int:personagem_id>/magias', methods=['POST'])
def adicionar_magia(personagem_id):
    if not _personagem_editavel(personagem_id):
        return redirect(url_for('index'))
    dados = _dados_do_formulario()
    if not dados['nome']:
        flash('Nome da magia é obrigatório.', 'danger')
    else:
        Magia.criar(personagem_id, dados)
        flash(f'{dados["nome"]} adicionada ao grimório.', 'success')
    return _voltar_para_ficha(personagem_id)


@bp.route('/magias/<int:magia_id>/editar', methods=['POST'])
def editar_magia(magia_id):
    magia = _magia_editavel(magia_id)
    if not magia:
        return redirect(url_for('index'))
    dados = _dados_do_formulario()
    if not dados['nome']:
        flash('Nome da magia é obrigatório.', 'danger')
    else:
        Magia.atualizar(magia_id, dados)
        flash('Magia atualizada.', 'success')
    return _voltar_para_ficha(magia['personagem_id'])


@bp.route('/magias/<int:magia_id>/remover', methods=['POST'])
def remover_magia(magia_id):
    magia = _magia_editavel(magia_id)
    if not magia:
        return redirect(url_for('index'))
    Magia.deletar(magia_id)
    flash(f'{magia["nome"]} removida do grimório.', 'success')
    return _voltar_para_ficha(magia['personagem_id'])
