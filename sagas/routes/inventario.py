# Catálogos, compra e inventário

from flask import jsonify, request
from decimal import Decimal
from models import Acervo, Atributos, Equipamento, Inventario, Pericia, Personagem
from flask import Blueprint

bp = Blueprint('inventario', __name__)
from utils.acesso import campanha_da_sessao, pode_gerenciar_personagem, verificar_admin, verificar_login
from utils.carga import _processar_inventario_personagem

@bp.route('/api/calcular-pontos', methods=['POST'])
def calcular_pontos():
    """Calcula pontos gastos em tempo real"""
    dados = request.json
    # Esta função já existe no models.py
    total = 0
    
    # Cálculo de pontos de atributos
    if 'atributos' in dados:
        total += Atributos._calcular_custo_atributos(
            dados['atributos'].get('ST', 10),
            dados['atributos'].get('DX', 10),
            dados['atributos'].get('IQ', 10),
            dados['atributos'].get('HT', 10)
        )
    
    return jsonify({'pontos_gastos': total})

# ==========================================
# APIs - Catálogo de Perícias
# ==========================================

def _campanha_id():
    campanha = campanha_da_sessao()
    return campanha['id'] if campanha else None


@bp.route('/api/pericias/catalogo')
def listar_pericias_catalogo():
    return jsonify(Acervo.listar_disponiveis('pericias', _campanha_id()))

# ==========================================
# APIs - Catálogo de Vantagens e Desvantagens
# ==========================================

@bp.route('/api/vantagens-desvantagens/catalogo')
def listar_vantagens_desvantagens_catalogo():
    """Retorna lista de vantagens e desvantagens do catálogo"""
    tipo = request.args.get('tipo', None)
    if tipo not in ('Vantagem', 'Desvantagem'):
        tipo = None
    return jsonify(Acervo.listar_disponiveis('vantagens', _campanha_id(), tipo=tipo))

@bp.route('/api/personagem/<int:personagem_id>/pericias/by-catalog', methods=['POST'])
def adicionar_pericia_por_catalogo(personagem_id):
    dados = request.json or {}
    try:
        cat_id = int(dados['catalogo_id'])
        pontos = int(dados.get('pontos_investidos', 1))
        
        # Valida pontos disponíveis
        if pontos > 0:
            personagem = Personagem.buscar_por_id(personagem_id)
            pontos_base = int(personagem.get('pontos_base') or 0)
            pontos_ganhos = int(personagem.get('pontos_ganhos') or 0)
            pontos_gastos_atual = int(personagem.get('pontos_gastos') or 0)
            pontos_disponiveis = (pontos_base + pontos_ganhos) - pontos_gastos_atual
            
            if pontos > pontos_disponiveis:
                return jsonify({
                    'success': False, 
                    'message': f'Pontos insuficientes. Disponível: {pontos_disponiveis}, Necessário: {pontos}'
                }), 400
        
        personagem = Personagem.buscar_por_id(personagem_id)
        if not personagem:
            return jsonify({'success': False, 'message': 'Personagem não encontrado'}), 404
        if not Acervo.disponivel('pericias', personagem.get('id_campanha'), cat_id):
            return jsonify({'success': False, 'message': 'Perícia não disponível nesta campanha'}), 404
        cat = Acervo.registro_efetivo('pericias', personagem.get('id_campanha'), cat_id)
        if not cat:
            return jsonify({'success': False, 'message': 'Perícia não encontrada no catálogo'}), 404
        
        Pericia.criar(
            personagem_id,
            cat['nome'],
            cat['atributo_base'],
            cat['dificuldade'],
            pontos
        )
        
        # Recalcula pontos gastos
        Personagem.recalcular_pontos_gastos(personagem_id)
        
        return jsonify({'success': True, 'message': 'Perícia adicionada com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==========================================
# APIs - Catálogo de Itens e Compras
# ==========================================

@bp.route('/api/itens/catalogo')
def listar_itens_catalogo():
    return jsonify(Acervo.listar_disponiveis('itens', _campanha_id()))


@bp.route('/api/personagem/<int:personagem_id>/inventario/by-catalog', methods=['POST'])
def adicionar_item_por_catalogo(personagem_id):
    if not verificar_login():
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401

    dados = request.json or {}
    try:
        catalogo_id = int(dados['catalogo_id'])
        quantidade = max(1, int(dados.get('quantidade', 1)))

        personagem = Personagem.buscar_por_id(personagem_id)
        if not personagem:
            return jsonify({'success': False, 'message': 'Personagem não encontrado'}), 404
        if not Acervo.disponivel('itens', personagem.get('id_campanha'), catalogo_id):
            return jsonify({'success': False, 'message': 'Item não disponível nesta campanha'}), 404

        item_catalogo = Acervo.registro_efetivo('itens', personagem.get('id_campanha'), catalogo_id)
        if not item_catalogo:
            return jsonify({'success': False, 'message': 'Item não encontrado no catálogo'}), 404

        preco_unitario = Decimal(str(item_catalogo.get('preco') or 0))
        peso_unitario = Decimal(str(item_catalogo.get('peso') or 0))

        dinheiro_atual = Decimal(str(personagem.get('dinheiro') or 0))
        custo_total = preco_unitario * quantidade

        if custo_total > dinheiro_atual:
            return jsonify({
                'success': False,
                'message': f'Dinheiro insuficiente. Disponível: {float(dinheiro_atual):.2f}, Necessário: {float(custo_total):.2f}'
            }), 400

        Inventario.criar(
            personagem_id=personagem_id,
            nome_item=item_catalogo['nome'],
            quantidade=quantidade,
            peso=float(peso_unitario),
            preco_unitario=float(preco_unitario),
            notas=item_catalogo.get('descricao', '') or '',
            tipo_item=item_catalogo.get('tipo_item', 'outro'),
            dano_bal_mod=item_catalogo.get('dano_bal_mod'),
            dano_bal_tipo=item_catalogo.get('dano_bal_tipo'),
            dano_gdp_mod=item_catalogo.get('dano_gdp_mod'),
            dano_gdp_tipo=item_catalogo.get('dano_gdp_tipo'),
            rd_mod=item_catalogo.get('rd_mod'),
            rd_tipo=item_catalogo.get('rd_tipo')
        )

        Personagem.atualizar_dinheiro(personagem_id, dinheiro_atual - custo_total)

        return jsonify({
            'success': True,
            'message': 'Item adicionado ao inventário!',
            'dinheiro_restante': float(dinheiro_atual - custo_total)
        })
    except KeyError:
        return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==========================================
# APIs - Inventário
# ==========================================

@bp.route('/api/personagem/<int:personagem_id>/inventario', methods=['GET'])
def listar_inventario(personagem_id):
    atributos = Atributos.buscar_por_personagem(personagem_id)
    dados = _processar_inventario_personagem(personagem_id, atributos)
    personagem = Personagem.buscar_por_id(personagem_id)
    pode_equipar = pode_gerenciar_personagem(personagem)
    itens = dados['itens']
    equipados = []
    nao_equipados = []
    for item in itens:
        tipo_item = (item.get('tipo_item') or '').lower()
        if item.get('slot') or tipo_item == 'equipamento':
            equipados.append(item)
        else:
            nao_equipados.append(item)
    return jsonify({
        'itens': nao_equipados,
        'equipados': equipados,
        'peso_total': dados['peso_total'],
        'valor_total': dados['valor_total'],
        'nivel_carga': dados['nivel_carga'],
        'efeitos': dados['efeitos'],
        'pode_equipar': pode_equipar,
        'dinheiro': float(personagem.get('dinheiro') or 0)
    })

@bp.route('/api/personagem/<int:personagem_id>/inventario', methods=['POST'])
def adicionar_item_inventario(personagem_id):
    if not verificar_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    dados = request.json or {}
    try:
        Inventario.criar(
            personagem_id=personagem_id,
            nome_item=dados['nome_item'],
            quantidade=int(dados.get('quantidade', 1)),
            peso=float(dados.get('peso', 0)),
            notas=dados.get('notas', ''),
            preco_unitario=float(dados.get('preco_unitario', 0)),
            tipo_item=dados.get('tipo_item', 'outro'),
            dano_bal_mod=dados.get('dano_bal_mod'),
            dano_bal_tipo=dados.get('dano_bal_tipo'),
            dano_gdp_mod=dados.get('dano_gdp_mod'),
            dano_gdp_tipo=dados.get('dano_gdp_tipo'),
            rd_mod=dados.get('rd_mod'),
            rd_tipo=dados.get('rd_tipo')
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/inventario/<int:item_id>', methods=['DELETE'])
def remover_item_inventario(item_id):
    if not verificar_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    try:
        Inventario.deletar(item_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/inventario/<int:item_id>/usar', methods=['POST'])
def atualizar_quantidade_em_uso(item_id):
    if not verificar_login():
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    dados = request.json or {}
    try:
        qtd = int(dados.get('quantidade_em_uso', 0))
        if qtd < 0:
            return jsonify({'success': False, 'message': 'Quantidade inválida'}), 400
        Inventario.atualizar_em_uso(item_id, qtd)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/inventario/<int:item_id>/consumir', methods=['POST'])
def consumir_item_inventario(item_id):
    if not verificar_login():
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    dados = request.json or {}
    try:
        qtd = int(dados.get('quantidade', 1))
        if qtd <= 0:
            return jsonify({'success': False, 'message': 'Quantidade inválida'}), 400
        Inventario.consumir(item_id, qtd)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/inventario/<int:item_id>/equipar', methods=['POST'])
def equipar_item_inventario(item_id):
    if not verificar_login():
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401

    dados = request.json or {}
    slot = (dados.get('slot') or '').strip()
    if not slot:
        return jsonify({'success': False, 'message': 'Slot é obrigatório'}), 400

    item = Inventario.buscar_por_id(item_id)
    if not item:
        return jsonify({'success': False, 'message': 'Item não encontrado'}), 404

    personagem = Personagem.buscar_por_id(item['personagem_id'])
    if not pode_gerenciar_personagem(personagem):
        return jsonify({'success': False, 'message': 'Sem permissão para equipar este item'}), 403

    try:
        Equipamento.equipar(personagem['id'], item_id, slot)
        return jsonify({'success': True, 'slot': slot})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/inventario/<int:item_id>/desequipar', methods=['POST'])
def desequipar_item_inventario(item_id):
    if not verificar_login():
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401

    item = Inventario.buscar_por_id(item_id)
    if not item:
        return jsonify({'success': False, 'message': 'Item não encontrado'}), 404

    personagem = Personagem.buscar_por_id(item['personagem_id'])
    if not pode_gerenciar_personagem(personagem):
        return jsonify({'success': False, 'message': 'Sem permissão para alterar este item'}), 403

    try:
        Equipamento.desequipar(item_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
