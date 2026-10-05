# APIs da ficha: vantagens, perícias, atributos e rolagens

from flask import jsonify, redirect, render_template, request, url_for
import os
from database import Database
from models import Atributos, Pericia, Personagem, VantagemDesvantagem, VantagemDesvantagemCatalogo
from routes.ficha import bp
from utils.acesso import verificar_login, exigir_login, exigir_admin

@bp.route('/api/personagem/<int:personagem_id>/vantagens', methods=['POST'])
def adicionar_vantagem(personagem_id):
    """Adiciona uma vantagem ou desvantagem"""
    dados = request.json
    
    try:
        nome_item = dados['nome_item']
        custo = int(dados.get('custo_em_pontos', 0))
        
        # Busca informações do catálogo para verificar se tem níveis
        from models import VantagemDesvantagemCatalogo
        item_catalogo = VantagemDesvantagemCatalogo.buscar_por_nome(nome_item)
        tem_niveis = False
        item_catalogo_info = None
        custo_base_catalogo = custo
        
        if item_catalogo and len(item_catalogo) > 0:
            item_catalogo_info = item_catalogo[0]
            custo_texto = item_catalogo_info.get('custo_texto', '') or ''
            custo_base_catalogo = item_catalogo_info.get('custo_base', custo)
            nome_item_lower = nome_item.lower()
            
            # Verifica se tem níveis:
            # 1. Contém palavras-chave no custo_texto
            # 2. Algumas vantagens conhecidas têm níveis mesmo sem indicador explícito
            tem_niveis = any(palavra in custo_texto.lower() for palavra in [
                '/nível', '/level', '/nivel', 'por nível', 'por level', 'por nivel',
                'pontos/nível', 'pontos/level', 'pontos por nível'
            ])
            
            # Vantagens conhecidas que sempre têm níveis
            vantagens_com_niveis = [
                'pf extra', 'pv extra', 'velocidade extra', 'resistência', 'sentidos aguçados',
                'vontade extra', 'vontade férrea', 'status', 'reputação', 'renda',
                'audição aguçada', 'olfato aguçado', 'paladar aguçado', 'tato aguçado'
            ]
            
            if any(vantagem in nome_item_lower for vantagem in vantagens_com_niveis):
                tem_niveis = True
        
        # Verifica se a vantagem já existe no personagem
        vantagens_existentes = VantagemDesvantagem.listar_por_personagem(personagem_id)
        vantagem_existente = None
        for vd in vantagens_existentes:
            if vd.get('nome_item', '').strip().lower() == nome_item.strip().lower():
                vantagem_existente = vd
                break
        
        # Se já existe e não tem níveis, bloqueia compra duplicada
        if vantagem_existente and not tem_niveis:
            return jsonify({
                'success': False,
                'message': f'Esta vantagem já foi comprada. Vantagens sem níveis não podem ser compradas mais de uma vez.'
            }), 400
        
        # Se tem níveis e já existe, soma os custos e aplica efeitos novamente
        if vantagem_existente and tem_niveis:
            custo_total = vantagem_existente.get('custo_em_pontos', 0) + custo
            notas_combinadas = f"{vantagem_existente.get('notas', '')} + {dados.get('notas', '')}".strip()
            
            # Aplica efeitos automáticos novamente (para somar PF_extra, PV_extra, etc)
            efeitos = VantagemDesvantagem._obter_efeitos_vantagem(nome_item)
            if efeitos:
                atributos = Atributos.buscar_por_personagem(personagem_id)
                if atributos:
                    PV_extra = atributos.get('PV_extra', 0) or 0
                    PF_extra = atributos.get('PF_extra', 0) or 0
                    percepcao_extra = atributos.get('percepcao_extra', 0) or 0
                    vontade_extra = atributos.get('vontade_extra', 0) or 0
                    
                    # Aplica efeitos novamente (soma)
                    if 'PV_extra' in efeitos:
                        PV_extra += efeitos['PV_extra']
                    if 'PF_extra' in efeitos:
                        PF_extra += efeitos['PF_extra']
                    if 'percepcao_extra' in efeitos:
                        percepcao_extra += efeitos['percepcao_extra']
                    if 'vontade_extra' in efeitos:
                        vontade_extra += efeitos['vontade_extra']
                    
                    # Atualiza os atributos
                    Atributos.atualizar(
                        personagem_id,
                        atributos['ST'],
                        atributos['DX'],
                        atributos['IQ'],
                        atributos['HT'],
                        PV_extra=PV_extra,
                        PF_extra=PF_extra,
                        percepcao_extra=percepcao_extra,
                        vontade_extra=vontade_extra
                    )
            
            # Atualiza a vantagem existente somando os custos
            query = """
                UPDATE vantagens_desvantagens 
                SET custo_em_pontos = %s, notas = %s
                WHERE id = %s
            """
            Database.execute_query(query, (custo_total, notas_combinadas, vantagem_existente['id']), fetch=False)
            
            # Recalcula pontos gastos
            Personagem.recalcular_pontos_gastos(personagem_id)
            
            # Calcula o nível baseado no custo base do catálogo
            nivel_atual = (custo_total // custo_base_catalogo) if custo_base_catalogo > 0 else 1
            return jsonify({
                'success': True, 
                'message': f'Vantagem atualizada! Custo total: {custo_total} pontos (nível {nivel_atual})'
            })
        
        # Valida pontos disponíveis (se for vantagem positiva)
        if custo > 0:
            personagem = Personagem.buscar_por_id(personagem_id)
            pontos_base = int(personagem.get('pontos_base') or 0)
            pontos_ganhos = int(personagem.get('pontos_ganhos') or 0)
            pontos_gastos_atual = int(personagem.get('pontos_gastos') or 0)
            pontos_disponiveis = (pontos_base + pontos_ganhos) - pontos_gastos_atual
            
            if custo > pontos_disponiveis:
                return jsonify({
                    'success': False, 
                    'message': f'Pontos insuficientes. Disponível: {pontos_disponiveis}, Necessário: {custo}'
                }), 400
        
        # Cria nova vantagem
        VantagemDesvantagem.criar(
            personagem_id,
            nome_item,
            custo,
            dados.get('notas', '')
        )
        
        # Recalcula pontos gastos
        Personagem.recalcular_pontos_gastos(personagem_id)
        
        return jsonify({'success': True, 'message': 'Vantagem/Desvantagem adicionada com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/vantagens/<int:vd_id>', methods=['DELETE'])
def deletar_vantagem(vd_id):
    """Remove uma vantagem ou desvantagem. Só permite remover desvantagens mediante pagamento de 1.5x."""
    try:
        # Verifica custo do item
        item = Database.execute_query("SELECT custo_em_pontos FROM vantagens_desvantagens WHERE id = %s", (vd_id,))
        if not item:
            return jsonify({'success': False, 'message': 'Item não encontrado'}), 404
        custo = int(item[0]['custo_em_pontos'] or 0)
        if custo >= 0:
            return jsonify({'success': False, 'message': 'Só é permitido remover desvantagens'}), 403
        dados = request.json or {}
        pontos_pagados = int(dados.get('pontos_pagados', 0))
        custo_minimo = int(1.5 * abs(custo))
        if pontos_pagados < custo_minimo:
            return jsonify({'success': False, 'message': f'É necessário pagar pelo menos {custo_minimo} pontos para remover esta desvantagem.'}), 400
        
        # Busca personagem_id antes de deletar
        query_personagem = "SELECT personagem_id FROM vantagens_desvantagens WHERE id = %s"
        result_personagem = Database.execute_query(query_personagem, (vd_id,))
        if not result_personagem:
            return jsonify({'success': False, 'message': 'Item não encontrado'}), 404
        personagem_id = result_personagem[0]['personagem_id']
        
        # Deleta a vantagem e reverte efeitos automáticos
        VantagemDesvantagem.deletar_com_efeitos(vd_id)
        
        # Recalcula pontos gastos
        Personagem.recalcular_pontos_gastos(personagem_id)
        
        return jsonify({'success': True, 'message': 'Desvantagem removida com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==========================================
# APIs - Perícias
# ==========================================

@bp.route('/api/personagem/<int:personagem_id>/pericias', methods=['POST'])
def adicionar_pericia(personagem_id):
    """Adiciona uma perícia"""
    dados = request.json
    
    try:
        pontos = int(dados.get('pontos_investidos', 0))
        
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
        
        Pericia.criar(
            personagem_id,
            dados['nome_pericia'],
            dados['atributo_base'],
            dados['dificuldade'],
            pontos
        )
        
        # Recalcula pontos gastos
        Personagem.recalcular_pontos_gastos(personagem_id)
        
        return jsonify({'success': True, 'message': 'Perícia adicionada com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/pericias/<int:pericia_id>', methods=['PUT'])
def atualizar_pericia(pericia_id):
    """Atualiza uma perícia"""
    dados = request.json
    
    try:
        pontos_novos = int(dados.get('pontos_investidos', 0))
        
        # Busca perícia atual para calcular diferença
        pericia_atual = Database.execute_query("SELECT personagem_id, pontos_investidos FROM pericias WHERE id = %s", (pericia_id,))
        if not pericia_atual:
            return jsonify({'success': False, 'message': 'Perícia não encontrada'}), 404
        
        personagem_id = pericia_atual[0]['personagem_id']
        pontos_atuais = int(pericia_atual[0]['pontos_investidos'] or 0)
        diferenca = pontos_novos - pontos_atuais
        
        # Valida pontos disponíveis se está aumentando
        if diferenca > 0:
            personagem = Personagem.buscar_por_id(personagem_id)
            pontos_base = int(personagem.get('pontos_base') or 0)
            pontos_ganhos = int(personagem.get('pontos_ganhos') or 0)
            pontos_gastos_atual = int(personagem.get('pontos_gastos') or 0)
            pontos_disponiveis = (pontos_base + pontos_ganhos) - pontos_gastos_atual
            
            if diferenca > pontos_disponiveis:
                return jsonify({
                    'success': False, 
                    'message': f'Pontos insuficientes. Disponível: {pontos_disponiveis}, Necessário: {diferenca}'
                }), 400
        
        Pericia.atualizar(pericia_id, pontos_novos)
        
        # Recalcula pontos gastos
        Personagem.recalcular_pontos_gastos(personagem_id)
        
        return jsonify({'success': True, 'message': 'Perícia atualizada com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/pericias/<int:pericia_id>', methods=['DELETE'])
def deletar_pericia(pericia_id):
    """Remove uma perícia"""
    try:
        # Busca personagem_id antes de deletar
        pericia = Database.execute_query("SELECT personagem_id FROM pericias WHERE id = %s", (pericia_id,))
        if not pericia:
            return jsonify({'success': False, 'message': 'Perícia não encontrada'}), 404
        
        personagem_id = pericia[0]['personagem_id']
        Pericia.deletar(pericia_id)
        
        # Recalcula pontos gastos
        Personagem.recalcular_pontos_gastos(personagem_id)
        
        return jsonify({'success': True, 'message': 'Perícia removida com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==========================================
# APIs - Atributos
# ==========================================

@bp.route('/api/personagem/<int:personagem_id>/atributos', methods=['PUT'])
def atualizar_atributos(personagem_id):
    """Atualiza apenas os atributos básicos (ST, DX, IQ, HT). 
    PV_extra, PF_extra, percepcao_extra e vontade_extra não podem ser alterados manualmente - só através de vantagens."""
    dados = request.json
    
    try:
        personagem = Personagem.buscar_por_id(personagem_id)
        if not personagem:
            return jsonify({'success': False, 'message': 'Personagem não encontrado.'}), 404

        atributos_atual = Atributos.buscar_por_personagem(personagem_id)
        if not atributos_atual:
            return jsonify({'success': False, 'message': 'Atributos do personagem não encontrados.'}), 404

        # Novos atributos solicitados
        novo_ST = int(dados['ST'])
        novo_DX = int(dados['DX'])
        novo_IQ = int(dados['IQ'])
        novo_HT = int(dados['HT'])

        # Mantém extras atuais para cálculo de custo
        PV_extra_atual = int(atributos_atual.get('PV_extra', 0) or 0)
        PF_extra_atual = int(atributos_atual.get('PF_extra', 0) or 0)
        percepcao_extra_atual = int(atributos_atual.get('percepcao_extra', 0) or 0)
        vontade_extra_atual = int(atributos_atual.get('vontade_extra', 0) or 0)

        # Calcula custo total projetado após a alteração
        custo_atributos_novo = Atributos._calcular_custo_atributos(
            novo_ST,
            novo_DX,
            novo_IQ,
            novo_HT,
            PV_extra_atual,
            PF_extra_atual,
            percepcao_extra_atual,
            vontade_extra_atual
        )

        # Soma vantagens/desvantagens e perícias atuais
        result_vd = Database.execute_query(
            """
            SELECT COALESCE(SUM(custo_em_pontos), 0) AS total
            FROM vantagens_desvantagens
            WHERE personagem_id = %s
            """,
            (personagem_id,)
        )
        custo_vd = int(result_vd[0]['total']) if result_vd else 0

        result_per = Database.execute_query(
            """
            SELECT COALESCE(SUM(pontos_investidos), 0) AS total
            FROM pericias
            WHERE personagem_id = %s
            """,
            (personagem_id,)
        )
        custo_pericias = int(result_per[0]['total']) if result_per else 0

        total_projetado = custo_atributos_novo + custo_vd + custo_pericias

        pontos_base = int(personagem.get('pontos_base') or 0)
        pontos_ganhos = int(personagem.get('pontos_ganhos') or 0)
        limite_pontos = pontos_base + pontos_ganhos

        if total_projetado > limite_pontos:
            faltam = total_projetado - limite_pontos
            return jsonify({
                'success': False,
                'message': f'Faltam {faltam} ponto(s) para aplicar as mudanças.',
                'faltando_pontos': faltam
            }), 400

        # Apenas atributos básicos podem ser alterados manualmente
        # Todos os extras (PV, PF, Percepção, Vontade) só podem ser alterados através de vantagens
        Atributos.atualizar(
            personagem_id,
            novo_ST,
            novo_DX,
            novo_IQ,
            novo_HT,
            PV_extra=None,  # Sempre None - mantém valor atual do banco
            PF_extra=None,  # Sempre None - mantém valor atual do banco
            percepcao_extra=None,  # Sempre None - mantém valor atual do banco
            vontade_extra=None  # Sempre None - mantém valor atual do banco
        )
        
        # Recalcula pontos gastos
        pontos_gastos_atualizados = Personagem.recalcular_pontos_gastos(personagem_id)
        
        # Recalcula atributos derivados
        atributos_atualizados = Atributos.buscar_por_personagem(personagem_id)
        vantagens = VantagemDesvantagem.listar_por_personagem(personagem_id)
        atributos_derivados = Atributos.calcular_atributos_derivados(atributos_atualizados, vantagens)

        pontos_disponiveis = limite_pontos - pontos_gastos_atualizados
        
        return jsonify({
            'success': True,
            'message': 'Atributos atualizados com sucesso!',
            'atributos': {
                'ST': atributos_atualizados['ST'],
                'DX': atributos_atualizados['DX'],
                'IQ': atributos_atualizados['IQ'],
                'HT': atributos_atualizados['HT']
            },
            'atributos_derivados': atributos_derivados,
            'pontos_resumo': {
                'pontos_base': pontos_base,
                'pontos_ganhos': pontos_ganhos,
                'pontos_gastos': pontos_gastos_atualizados,
                'pontos_disponiveis': pontos_disponiveis
            }
        })
    except KeyError as e:
        return jsonify({'success': False, 'message': f'Dado ausente: {str(e)}'}), 400
    except ValueError:
        return jsonify({'success': False, 'message': 'Valores inválidos para atributos.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==========================================
# API - Rolagens de Dados
# ==========================================

@bp.route('/api/rolar/<int:alvo>', methods=['POST'])
def rolar_dados(alvo):
    """Executa uma rolagem de dados 3d6"""
    dados = request.json if request.json else {}
    bonus = dados.get('bonus', 0)
    
    import random
    
    # Rola 3d6
    resultados = [random.randint(1, 6) for _ in range(3)]
    total = sum(resultados) + bonus
    
    # Determina o resultado (GURPS: crítico é 3-4, falha crítica é 17-18)
    if total <= 4:
        # Crítico (3 ou 4): sempre sucesso, independente do alvo
        resultado = 'crítico'
        sucesso = True
    elif total >= 17:
        # Falha crítica (17 ou 18): sempre falha
        resultado = 'falha_crítica'
        sucesso = False
    elif total <= alvo:
        resultado = 'sucesso'
        sucesso = True
    else:
        resultado = 'falha'
        sucesso = False
    
    # Persiste log
    try:
        Database.execute_query(
            """
            INSERT INTO rolagens_log (personagem_id, tipo, alvo, bonus, resultados, total, sucesso)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                dados.get('personagem_id'),
                '3d6',
                int(alvo),
                int(bonus or 0),
                ','.join(map(str, resultados)),
                int(total),
                bool(sucesso)
            ),
            fetch=False
        )
    except Exception:
        pass

    return jsonify({
        'resultados': resultados,
        'total': total,
        'alvo': alvo,
        'resultado': resultado,
        'sucesso': sucesso,
        'bonus': bonus
    })

@bp.route('/ultimas-rolagens')
@exigir_login
def ultimas_rolagens():
    linhas = Database.execute_query(
        """
        SELECT rl.*, p.nome AS personagem_nome
        FROM rolagens_log rl
        LEFT JOIN personagens p ON p.id = rl.personagem_id
        ORDER BY rl.created_at DESC
        LIMIT 100
        """
    )
    return render_template('ultimas_rolagens.html', rolagens=linhas)
