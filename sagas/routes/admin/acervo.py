# O mestre marca o que a campanha aberta usa do acervo.

import mysql.connector
from flask import flash, redirect, render_template, request, url_for

from models.acervo import Acervo
from routes.admin import bp
from utils.acesso import exigir_admin, exigir_campanha


def _voltar(aba, busca):
    return redirect(url_for('admin.admin_acervo', aba=aba, q=busca or None))


@bp.route('/admin/acervo')
@exigir_admin
def admin_acervo():
    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('campanhas.listar_campanhas'))
    aba = request.args.get('aba') or 'pericias'
    if aba not in dict(Acervo.abas()):
        aba = 'pericias'
    busca = (request.args.get('q') or '').strip()
    return render_template(
        'admin_acervo.html',
        campanha=campanha,
        aba=aba,
        spec=Acervo.spec(aba),
        abas=Acervo.abas(),
        busca=busca,
        itens=Acervo.listar_mestre(aba, campanha['id'], busca),
    )


@bp.route('/admin/acervo/<aba>/<int:item_id>', methods=['POST'])
@exigir_admin
def admin_acervo_marcar(aba, item_id):
    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('campanhas.listar_campanhas'))
    busca = (request.form.get('q') or '').strip()
    if aba not in dict(Acervo.abas()):
        return _voltar('pericias', busca)
    marcou = Acervo.definir(aba, campanha['id'], item_id, request.form.get('marcar') == '1')
    if not marcou:
        flash('Esse registro é desta campanha e permanece nela.', 'info')
    return _voltar(aba, busca)


@bp.route('/admin/acervo/<aba>/novo', methods=['POST'])
@exigir_admin
def admin_acervo_novo(aba):
    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('campanhas.listar_campanhas'))
    busca = (request.form.get('q') or '').strip()
    if aba not in dict(Acervo.abas()):
        return _voltar('pericias', busca)
    try:
        Acervo.criar(aba, campanha['id'], request.form)
        flash('Registro acrescentado só nesta campanha.', 'success')
    except ValueError as erro:
        flash(str(erro), 'danger')
    except mysql.connector.Error as erro:
        if erro.errno == 1062:
            flash('Já existe um registro com esse nome.', 'danger')
        else:
            raise
    return _voltar(aba, busca)
