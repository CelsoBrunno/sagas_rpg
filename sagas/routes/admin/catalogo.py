# Catálogo da campanha aberta: ver o banco, marcar, ajustar e acrescentar registros próprios.

import mysql.connector
from flask import flash, redirect, render_template, request, url_for

from models.acervo import Acervo
from routes.admin import bp
from utils.acesso import exigir_admin, exigir_campanha


def _voltar(aba, adicionados):
    busca = (request.form.get('q') or '').strip()
    return redirect(url_for(
        'admin.admin_catalogo',
        aba=aba,
        adicionados=1 if adicionados else None,
        q=busca or None,
    ))


@bp.route('/admin/catalogo')
@exigir_admin
def admin_catalogo():
    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('campanhas.listar_campanhas'))
    aba = request.args.get('aba') or 'itens'
    if aba not in dict(Acervo.abas()):
        aba = 'itens'
    so_adicionados = request.args.get('adicionados') == '1'
    busca = (request.args.get('q') or '').strip()
    return render_template(
        'admin_catalogo.html',
        campanha=campanha,
        aba=aba,
        spec=Acervo.spec(aba),
        abas=Acervo.abas(),
        adicionados=so_adicionados,
        busca=busca,
        itens=Acervo.listar_catalogo(aba, campanha['id'], so_adicionados, busca),
    )


@bp.route('/admin/catalogo/<aba>/<int:item_id>/adicionar', methods=['POST'])
@exigir_admin
def admin_catalogo_adicionar(aba, item_id):
    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('campanhas.listar_campanhas'))
    if aba in dict(Acervo.abas()) and Acervo.adicionar_a_campanha(aba, campanha['id'], item_id):
        flash('Adicionado à campanha.', 'success')
    else:
        flash('Não foi possível adicionar.', 'danger')
    return _voltar(aba, False)


@bp.route('/admin/catalogo/<aba>/<int:item_id>/ajuste', methods=['POST'])
@exigir_admin
def admin_catalogo_ajuste(aba, item_id):
    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('campanhas.listar_campanhas'))
    if aba in dict(Acervo.abas()) and Acervo.salvar_ajustes(aba, campanha['id'], item_id, request.form):
        flash('Ajuste salvo só nesta campanha.', 'success')
    else:
        flash('Não foi possível salvar.', 'danger')
    return _voltar(aba, True)


@bp.route('/admin/catalogo/<aba>/<int:item_id>/restaurar', methods=['POST'])
@exigir_admin
def admin_catalogo_restaurar(aba, item_id):
    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('campanhas.listar_campanhas'))
    if aba in dict(Acervo.abas()):
        Acervo.restaurar_ajustes(aba, campanha['id'], item_id)
        flash('Voltou ao padrão do catálogo.', 'success')
    return _voltar(aba, True)


@bp.route('/admin/catalogo/<aba>/<int:item_id>/remover', methods=['POST'])
@exigir_admin
def admin_catalogo_remover(aba, item_id):
    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('campanhas.listar_campanhas'))
    if aba in dict(Acervo.abas()):
        Acervo.remover_da_campanha(aba, campanha['id'], item_id)
        flash('Removido da campanha.', 'success')
    return _voltar(aba, True)


@bp.route('/admin/catalogo/<aba>/novo', methods=['POST'])
@exigir_admin
def admin_catalogo_novo(aba):
    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('campanhas.listar_campanhas'))
    if aba not in dict(Acervo.abas()):
        return _voltar('itens', False)
    try:
        Acervo.criar(aba, campanha['id'], request.form)
        flash('Registro acrescentado só nesta campanha.', 'success')
    except ValueError as erro:
        flash(str(erro), 'danger')
        return _voltar(aba, False)
    except mysql.connector.Error as erro:
        if erro.errno == 1062:
            flash('Já existe um registro com esse nome.', 'danger')
            return _voltar(aba, False)
        raise
    return _voltar(aba, True)
