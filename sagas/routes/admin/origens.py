# Admin: raças e classes

import json

from flask import flash, redirect, render_template, request, url_for

from models import Classe, PericiaCatalogo, Raca, VantagemDesvantagemCatalogo
from routes.admin import bp
from utils.acesso import campanha_da_sessao, exigir_admin, exigir_campanha, pertence_a_campanha_ativa

ORIGENS = {
    'raca': {
        'modelo': Raca,
        'rotulo': 'Raça',
        'chave_lista': 'racas',
        'chave_registro': 'raca',
        'lista': 'admin.admin_racas_lista',
    },
    'classe': {
        'modelo': Classe,
        'rotulo': 'Classe',
        'chave_lista': 'classes',
        'chave_registro': 'classe',
        'lista': 'admin.admin_classes_lista',
    },
}


def _json_do_formulario(campo):
    texto = request.form.get(campo, '')
    if not texto:
        return None
    try:
        ids = json.loads(texto)
    except (TypeError, ValueError):
        return None
    if isinstance(ids, list) and ids:
        return texto
    return None


def _ids_salvos(registro, campo):
    if not registro or not registro.get(campo):
        return []
    try:
        ids = json.loads(registro[campo])
    except (TypeError, ValueError):
        return []
    return ids if isinstance(ids, list) else []


def _dados_do_formulario(campanha_id=None):
    dados = {
        'nome': request.form.get('nome'),
        'descricao': request.form.get('descricao', ''),
        'bonus_st': int(request.form.get('bonus_st', 0)),
        'bonus_dx': int(request.form.get('bonus_dx', 0)),
        'bonus_iq': int(request.form.get('bonus_iq', 0)),
        'bonus_ht': int(request.form.get('bonus_ht', 0)),
        'bonus_pv_extra': int(request.form.get('bonus_pv_extra', 0)),
        'bonus_pf_extra': int(request.form.get('bonus_pf_extra', 0)),
        'bonus_percepcao_extra': int(request.form.get('bonus_percepcao_extra', 0)),
        'bonus_vontade_extra': int(request.form.get('bonus_vontade_extra', 0)),
        'custo_em_pontos': int(request.form.get('custo_em_pontos', 0)),
        'vantagens_automaticas': _json_do_formulario('vantagens_automaticas'),
        'pericias_automaticas': _json_do_formulario('pericias_automaticas'),
        'observacoes': request.form.get('observacoes', ''),
        'is_active': request.form.get('is_active') == 'on',
    }
    if campanha_id is not None:
        dados['id_campanha'] = campanha_id
    return dados


def _listar(tipo):
    origem = ORIGENS[tipo]
    campanha = campanha_da_sessao()
    registros = origem['modelo'].listar_por_campanha(campanha['id']) if campanha else []
    return render_template(
        'admin_bonus_lista.html',
        sem_campanha=campanha is None,
        **{origem['chave_lista']: registros},
    )


def _formulario(tipo, registro_id=None):
    origem = ORIGENS[tipo]
    modelo = origem['modelo']
    destino = origem['lista']
    rotulo = origem['rotulo']
    registro = None
    campanha = None

    if registro_id is None:
        campanha = exigir_campanha()
        if not campanha:
            return redirect(url_for('campanhas.listar_campanhas'))
    else:
        registro = modelo.buscar_por_id(registro_id)
        if not registro or not pertence_a_campanha_ativa(registro):
            flash(f'{rotulo} não encontrada nesta campanha.', 'danger')
            return redirect(url_for(destino))

    if request.method == 'POST':
        try:
            dados = _dados_do_formulario(campanha['id'] if campanha else None)
            if registro_id is None:
                modelo.criar(dados)
                flash(f'{rotulo} criada com sucesso!', 'success')
            else:
                modelo.atualizar(registro_id, dados)
                flash(f'{rotulo} atualizada com sucesso!', 'success')
            return redirect(url_for(destino))
        except Exception as erro:
            acao = 'criar' if registro_id is None else 'atualizar'
            flash(f'Erro ao {acao} {rotulo.lower()}: {erro}', 'danger')

    return render_template(
        'admin_bonus_form.html',
        vantagens=VantagemDesvantagemCatalogo.listar_vantagens(),
        pericias=PericiaCatalogo.listar_todas(),
        vantagens_selecionadas=_ids_salvos(registro, 'vantagens_automaticas'),
        pericias_selecionadas=_ids_salvos(registro, 'pericias_automaticas'),
        **{origem['chave_registro']: registro},
    )


def _remover(tipo, registro_id):
    origem = ORIGENS[tipo]
    modelo = origem['modelo']
    destino = origem['lista']
    rotulo = origem['rotulo']
    if not pertence_a_campanha_ativa(modelo.buscar_por_id(registro_id)):
        flash(f'{rotulo} não encontrada nesta campanha.', 'danger')
        return redirect(url_for(destino))
    try:
        modelo.deletar(registro_id)
        flash(f'{rotulo} deletada com sucesso!', 'success')
    except Exception as erro:
        flash(f'Erro ao deletar {rotulo.lower()}: {erro}', 'danger')
    return redirect(url_for(destino))


@bp.route('/admin/racas')
@exigir_admin
def admin_racas_lista():
    return _listar('raca')


@bp.route('/admin/racas/novo', methods=['GET', 'POST'])
@exigir_admin(mensagem='Acesso restrito ao Mestre (admin).', destino='admin.admin_racas_lista')
def admin_racas_novo():
    return _formulario('raca')


@bp.route('/admin/racas/<int:id>/editar', methods=['GET', 'POST'])
@exigir_admin(mensagem='Acesso restrito ao Mestre (admin).', destino='admin.admin_racas_lista')
def admin_racas_editar(id):
    return _formulario('raca', id)


@bp.route('/admin/racas/<int:id>/deletar', methods=['POST'])
@exigir_admin(mensagem='Acesso restrito ao Mestre (admin).', destino='admin.admin_racas_lista')
def admin_racas_deletar(id):
    return _remover('raca', id)


@bp.route('/admin/classes')
@exigir_admin
def admin_classes_lista():
    return _listar('classe')


@bp.route('/admin/classes/novo', methods=['GET', 'POST'])
@exigir_admin(mensagem='Acesso restrito ao Mestre (admin).', destino='admin.admin_classes_lista')
def admin_classes_novo():
    return _formulario('classe')


@bp.route('/admin/classes/<int:id>/editar', methods=['GET', 'POST'])
@exigir_admin(mensagem='Acesso restrito ao Mestre (admin).', destino='admin.admin_classes_lista')
def admin_classes_editar(id):
    return _formulario('classe', id)


@bp.route('/admin/classes/<int:id>/deletar', methods=['POST'])
@exigir_admin(mensagem='Acesso restrito ao Mestre (admin).', destino='admin.admin_classes_lista')
def admin_classes_deletar(id):
    return _remover('classe', id)
