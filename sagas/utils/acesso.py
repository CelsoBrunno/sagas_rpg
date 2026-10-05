# ==========================================
# Helpers de sessão: login, admin e campanha ativa
# ==========================================

from functools import wraps

from flask import flash, redirect, session, url_for

from models.campanha import Campanha


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


def pode_gerenciar_personagem(personagem):
    """Mestre, o dono da ficha, ou quem recebeu acesso temporário ainda válido."""
    if not personagem:
        return False
    if verificar_admin():
        return True
    try:
        usuario_id = int(session.get('user_id', 0))
        dono_id = personagem.get('id_usuario_jogador')
        if dono_id is not None and int(dono_id) == usuario_id:
            return True
    except (TypeError, ValueError):
        return False
    from models.acesso_temporario import AcessoTemporario
    return AcessoTemporario.esta_ativo(personagem.get('id'), session.get('user_id'))


def exigir_login(view=None, *, mensagem=None, categoria='info'):
    """Redireciona para o login. Sem mensagem, só redireciona."""
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if not verificar_login():
                if mensagem:
                    flash(mensagem, categoria)
                return redirect(url_for('auth.login'))
            return fn(*args, **kwargs)
        return wrapped

    if view is not None and callable(view):
        return decorator(view)
    return decorator


def exigir_admin(view=None, *, mensagem='Acesso restrito ao Mestre (admin).', destino='ficha.index'):
    """Redireciona quem não é mestre. A mensagem e o destino acompanham a rota."""
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if not verificar_admin():
                flash(mensagem, 'danger')
                return redirect(url_for(destino))
            return fn(*args, **kwargs)
        return wrapped

    if view is not None and callable(view):
        return decorator(view)
    return decorator


def pertence_a_campanha_ativa(registro):
    """Confere se o registro é da campanha escolhida."""
    campanha = campanha_da_sessao()
    if not campanha or not registro:
        return False
    try:
        return int(registro.get('id_campanha') or 0) == int(campanha['id'])
    except (TypeError, ValueError):
        return False
