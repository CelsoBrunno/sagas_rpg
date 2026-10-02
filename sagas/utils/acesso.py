# ==========================================
# Helpers de sessão: login, admin e campanha ativa
# ==========================================

from flask import session, flash

from models import Campanha


def verificar_admin():
    """Verifica se o usuário logado é admin"""
    if not session.get('user_id'):
        return False
    return session.get('role') == 'admin'


def verificar_login():
    """Verifica se o usuário está logado"""
    return 'user_id' in session


def campanha_da_sessao():
    """Campanha escolhida nesta sessão, ou None."""
    campanha_id = session.get('campanha_id')
    if not campanha_id:
        return None
    campanha = Campanha.buscar_por_id(campanha_id)
    if not campanha:
        session.pop('campanha_id', None)
        return None
    return campanha


def exigir_campanha():
    """Exige uma campanha escolhida e avisa quando falta."""
    campanha = campanha_da_sessao()
    if not campanha:
        flash('Escolha uma campanha antes de continuar.', 'info')
    return campanha


def pertence_a_campanha_ativa(registro):
    """Confere se o registro é da campanha escolhida."""
    campanha = campanha_da_sessao()
    if not campanha or not registro:
        return False
    try:
        return int(registro.get('id_campanha') or 0) == int(campanha['id'])
    except (TypeError, ValueError):
        return False
