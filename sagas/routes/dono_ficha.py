# ==========================================
# Dono da ficha: o mestre entrega um personagem a um usuário,
# que passa a usá-lo como se fosse dele.
# Acesso temporário não troca o dono: vale só até o prazo.
# ==========================================

from datetime import datetime

from flask import Blueprint, request, redirect, url_for, flash

from models import Personagem, Usuario
from models.acesso_temporario import AcessoTemporario
from utils.acesso import pertence_a_campanha_ativa, exigir_admin

bp = Blueprint('dono_ficha', __name__)


@bp.route('/personagem/<int:personagem_id>/dono', methods=['POST'])
@exigir_admin(mensagem='Apenas o mestre pode atribuir fichas.', destino='ficha.index')
def definir_dono(personagem_id):
    personagem = Personagem.buscar_por_id(personagem_id)
    if not personagem or (personagem.get('id_campanha') and not pertence_a_campanha_ativa(personagem)):
        flash('Personagem não encontrado nesta campanha.', 'danger')
        return redirect(url_for('ficha.index'))

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
    return redirect(url_for('ficha.ver_personagem', id=personagem_id))


def _ficha_da_campanha(personagem_id):
    personagem = Personagem.buscar_por_id(personagem_id)
    if not personagem or (personagem.get('id_campanha') and not pertence_a_campanha_ativa(personagem)):
        flash('Personagem não encontrado nesta campanha.', 'danger')
        return None
    return personagem


@bp.route('/personagem/<int:personagem_id>/acesso-temporario', methods=['POST'])
@exigir_admin(mensagem='Apenas o mestre pode liberar uma ficha.', destino='ficha.index')
def liberar_acesso(personagem_id):
    """Libera a ficha para um jogador até o horário informado. A ficha própria dele continua."""
    personagem = _ficha_da_campanha(personagem_id)
    if not personagem:
        return redirect(url_for('ficha.index'))

    usuario_id = request.form.get('usuario_id', type=int)
    usuario = Usuario.buscar_por_id(usuario_id) if usuario_id else None
    if not usuario:
        flash('Escolha o jogador que vai usar esta ficha.', 'danger')
        return redirect(url_for('ficha.ver_personagem', id=personagem_id))

    dono_id = personagem.get('id_usuario_jogador')
    if dono_id is not None and int(dono_id) == int(usuario_id):
        flash(f'{usuario["username"]} já é o dono desta ficha.', 'info')
        return redirect(url_for('ficha.ver_personagem', id=personagem_id))

    try:
        expira = datetime.strptime((request.form.get('expira_em') or '')[:16], '%Y-%m-%dT%H:%M')
    except ValueError:
        flash('Informe até quando o jogador pode usar esta ficha.', 'danger')
        return redirect(url_for('ficha.ver_personagem', id=personagem_id))

    if expira <= datetime.now():
        flash('O prazo precisa ser no futuro.', 'danger')
        return redirect(url_for('ficha.ver_personagem', id=personagem_id))

    AcessoTemporario.liberar(personagem_id, usuario_id, expira)
    flash(
        f'{usuario["username"]} pode usar {personagem["nome"]} até {expira.strftime("%d/%m/%Y %H:%M")}.',
        'success',
    )
    return redirect(url_for('ficha.ver_personagem', id=personagem_id))


@bp.route('/personagem/<int:personagem_id>/acesso-temporario/encerrar', methods=['POST'])
@exigir_admin(mensagem='Apenas o mestre pode encerrar o acesso.', destino='ficha.index')
def encerrar_acesso(personagem_id):
    personagem = _ficha_da_campanha(personagem_id)
    if not personagem:
        return redirect(url_for('ficha.index'))

    usuario_id = request.form.get('usuario_id', type=int)
    if usuario_id:
        AcessoTemporario.encerrar(personagem_id, usuario_id)
        flash(f'O acesso temporário a {personagem["nome"]} foi encerrado.', 'success')
    return redirect(url_for('ficha.ver_personagem', id=personagem_id))
