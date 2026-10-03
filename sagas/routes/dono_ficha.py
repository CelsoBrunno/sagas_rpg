# ==========================================
# Dono da ficha: o mestre entrega um personagem a um usuário,
# que passa a usá-lo como se fosse dele.
# ==========================================

from flask import Blueprint, request, redirect, url_for, flash

from models import Personagem, Usuario
from utils.acesso import verificar_admin, pertence_a_campanha_ativa

bp = Blueprint('dono_ficha', __name__)


@bp.route('/personagem/<int:personagem_id>/dono', methods=['POST'])
def definir_dono(personagem_id):
    if not verificar_admin():
        flash('Apenas o mestre pode atribuir fichas.', 'danger')
        return redirect(url_for('index'))
    personagem = Personagem.buscar_por_id(personagem_id)
    if not personagem or (personagem.get('id_campanha') and not pertence_a_campanha_ativa(personagem)):
        flash('Personagem não encontrado nesta campanha.', 'danger')
        return redirect(url_for('index'))

    usuario_id = request.form.get('usuario_id', type=int)
    if usuario_id is None:
        Personagem.definir_dono(personagem_id, None)
        flash(f'{personagem["nome"]} não tem mais dono e voltou a ser NPC.', 'success')
    else:
        usuario = Usuario.buscar_por_id(usuario_id)
        if not usuario:
            flash('Usuário não encontrado.', 'danger')
        else:
            Personagem.definir_dono(personagem_id, usuario_id)
            flash(f'{personagem["nome"]} agora é de {usuario["username"]}.', 'success')
    return redirect(url_for('ver_personagem', id=personagem_id))
