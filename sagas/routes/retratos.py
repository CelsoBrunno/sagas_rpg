# ==========================================
# Retrato das fichas de personagem
# Fichas de criaturas usam a capa do bestiário.
# ==========================================

from flask import Blueprint, request, redirect, url_for, flash

from models import Personagem, Imagem, Bestiario
from utils.acesso import pode_gerenciar_personagem, pertence_a_campanha_ativa
from utils.uploads import salvar_imagem, remover_imagem

bp = Blueprint('retratos', __name__)

ENTIDADE = 'personagem'


def retratos_da_campanha(campanha_id, personagens):
    """{personagem_id: url} para os cards da lista de personagens."""
    ids = [p['id'] for p in personagens]
    retratos = Imagem.primeiras_por_entidades(ENTIDADE, ids)
    if campanha_id:
        retratos.update(Bestiario.capas_por_ficha(campanha_id))
    return retratos


def retrato_do_personagem(personagem):
    """(url, vem_do_bestiario) do retrato de uma ficha."""
    if personagem.get('id_campanha'):
        capa = Bestiario.capas_por_ficha(personagem['id_campanha']).get(personagem['id'])
        if capa:
            return capa, True
    imagem = Imagem.primeiras_por_entidades(ENTIDADE, [personagem['id']]).get(personagem['id'])
    return imagem, False


def remover_retratos(personagem_id):
    for imagem in Imagem.buscar_por_entidade(ENTIDADE, personagem_id) or []:
        Imagem.deletar(imagem['id'])
        remover_imagem(imagem['path_url'])


def _personagem_editavel(personagem_id):
    personagem = Personagem.buscar_por_id(personagem_id)
    if not personagem or (personagem.get('id_campanha') and not pertence_a_campanha_ativa(personagem)):
        flash('Personagem não encontrado nesta campanha.', 'danger')
        return None
    if not pode_gerenciar_personagem(personagem):
        flash('Só o mestre ou o dono da ficha pode trocar o retrato.', 'danger')
        return None
    return personagem


@bp.route('/personagem/<int:personagem_id>/retrato', methods=['POST'])
def enviar_retrato(personagem_id):
    personagem = _personagem_editavel(personagem_id)
    if not personagem:
        return redirect(url_for('ficha.index'))
    imagem_url = salvar_imagem(request.files.get('retrato'), 'retrato')
    if not imagem_url:
        flash('Escolha uma imagem PNG, JPG, GIF ou WEBP.', 'danger')
        return redirect(url_for('ficha.ver_personagem', id=personagem_id))
    remover_retratos(personagem_id)
    Imagem.criar({
        'path_url': imagem_url,
        'alt_text': personagem['nome'],
        'titulo': 'Retrato',
        'entidade_tipo': ENTIDADE,
        'entidade_id': personagem_id,
    })
    flash('Retrato atualizado.', 'success')
    return redirect(url_for('ficha.ver_personagem', id=personagem_id))


@bp.route('/personagem/<int:personagem_id>/retrato/remover', methods=['POST'])
def remover_retrato(personagem_id):
    if _personagem_editavel(personagem_id):
        remover_retratos(personagem_id)
        flash('Retrato removido.', 'success')
    return redirect(url_for('ficha.ver_personagem', id=personagem_id))
