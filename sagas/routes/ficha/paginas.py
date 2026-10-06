# Rotas de ficha: lista, criação e visualização

from flask import flash, jsonify, make_response, redirect, render_template, request, session, url_for
import os
from database import Database
from config import Config
from models import Acervo, Atributos, Bestiario, Classe, Magia, Pericia, PericiaCatalogo, Personagem, Raca, SessaoLog, Usuario, VantagemDesvantagem, VantagemDesvantagemCatalogo
from routes.ficha import bp
from routes.retratos import remover_retratos, retrato_do_personagem, retratos_da_campanha
from models.acesso_temporario import AcessoTemporario
from utils.acesso import campanha_da_sessao, exigir_campanha, pertence_a_campanha_ativa, pode_gerenciar_personagem, verificar_admin, verificar_login, exigir_login, exigir_admin
from utils.carga import _obter_valor_atributo_para_pericia, _processar_inventario_personagem

@bp.route('/')
@exigir_login(mensagem='Faça login para acessar o sistema.', categoria='info')
def index():
    """Página inicial - lista de personagens"""
    
    campanha = campanha_da_sessao()
    personagens = Personagem.listar_por_campanha(campanha['id']) if campanha else []
    if campanha and not verificar_admin():
        user_id = session.get('user_id')
        emprestimos = AcessoTemporario.mapa_ativos(user_id)
        personagens = [p for p in personagens if pode_gerenciar_personagem(p)]
        ocultas = Bestiario.fichas_bloqueadas(campanha['id'])
        visiveis = []
        for p in personagens:
            dono = p.get('id_usuario_jogador')
            e_dono = dono is not None and int(dono) == int(user_id)
            if p['id'] in ocultas and p['id'] not in emprestimos and not e_dono:
                continue
            if p['id'] in emprestimos and not e_dono:
                p['acesso_ate'] = emprestimos[p['id']]
            visiveis.append(p)
        personagens = visiveis
    retratos = retratos_da_campanha(campanha['id'], personagens) if campanha else {}
    return render_template('index.html', personagens=personagens, sem_campanha=campanha is None,
                           retratos=retratos)

@bp.route('/personagem/<int:id>')
def ver_personagem(id):
    """Visualiza uma ficha de personagem completa"""
    personagem = Personagem.buscar_por_id(id)
    
    if not personagem:
        flash('Personagem não encontrado.', 'danger')
        return redirect(url_for('ficha.index'))

    if personagem.get('id_campanha') and not pertence_a_campanha_ativa(personagem):
        flash('Esse personagem pertence a outra campanha.', 'danger')
        return redirect(url_for('ficha.index'))

    if not pode_gerenciar_personagem(personagem):
        if AcessoTemporario.expirou(id, session.get('user_id')):
            flash('O prazo para usar esta ficha acabou.', 'info')
        else:
            flash('Esta ficha não está atribuída a você.', 'danger')
        return redirect(url_for('ficha.index'))

    if _ficha_oculta(personagem):
        flash('Esta criatura ainda não foi revelada.', 'info')
        return redirect(url_for('bestiario.listar_bestiario'))

    pode_equipar = pode_gerenciar_personagem(personagem)
    
    atributos = Atributos.buscar_por_personagem(id)
    vantagens = VantagemDesvantagem.listar_por_personagem(id)
    atributos_derivados = Atributos.calcular_atributos_derivados(atributos, vantagens) if atributos else {}

    pericias = Pericia.listar_por_personagem(id)

    pericias_processadas = []
    if atributos:
        iq_base = atributos.get('IQ', 10)
        percepcao_extra = atributos.get('percepcao_extra') or 0
        vontade_extra = atributos.get('vontade_extra') or 0
        percepcao_calculada = atributos_derivados.get('percepcao') if atributos_derivados else iq_base + percepcao_extra
        vontade_calculada = atributos_derivados.get('vontade') if atributos_derivados else iq_base + vontade_extra
        atributos['Per'] = percepcao_calculada
        atributos['Will'] = vontade_calculada

    for pericia in pericias:
        atributo_codigo = pericia.get('atributo_base')
        atributo_valor = _obter_valor_atributo_para_pericia(atributos, atributo_codigo)
        nivel_calculado = Pericia._calcular_nivel_habilidade(
            atributo_valor,
            pericia.get('dificuldade'),
            pericia.get('pontos_investidos')
        )

        if pericia.get('nivel_habilidade_calculado') != nivel_calculado:
            pericia['nivel_habilidade_calculado'] = nivel_calculado

        pericia['atributo_valor_atual'] = atributo_valor
        pericia['ajuste_nivel'] = nivel_calculado - atributo_valor if atributo_valor is not None else None
        pericias_processadas.append(pericia)

    inventario_info = _processar_inventario_personagem(id, atributos)
    itens_inventario = inventario_info['itens']
    peso_total = inventario_info['peso_total']
    valor_total_inventario = inventario_info['valor_total']
    nivel_carga = inventario_info['nivel_carga']
    efeitos_itens = inventario_info['efeitos']

    bonus_itens = efeitos_itens.get('bonus', {}) if efeitos_itens else {}
    dr_adicional = bonus_itens.get('dr', 0)
    dr_base = atributos_derivados.get('dr_base', 0)
    atributos_derivados['dr_base'] = dr_base
    atributos_derivados['dr_total'] = dr_base + dr_adicional
    
    equipamentos = []
    itens_inventario_nao_equipados = []
    for item in itens_inventario:
        tipo_item = (item.get('tipo_item') or '').lower()
        if item.get('slot') or tipo_item == 'equipamento':
            equipamentos.append(item)
        else:
            itens_inventario_nao_equipados.append(item)

    # Resumo de pontos (GURPS)
    pontos_base = int(personagem.get('pontos_base') or 0)
    pontos_ganhos = int(personagem.get('pontos_ganhos') or 0)
    pontos_gastos = int(personagem.get('pontos_gastos') or 0)
    pontos_disponiveis_ficha = (pontos_base + pontos_ganhos) - pontos_gastos
    
    # Pontos disponíveis do usuário (concedidos pelo admin)
    # Se o personagem tem um usuário associado, busca os pontos do usuário
    pontos_disponiveis_usuario = None
    if personagem.get('id_usuario_jogador'):
        pontos_disponiveis_usuario = Usuario.get_pontos_disponiveis(personagem['id_usuario_jogador'])

    # Histórico de evolução (pontos por sessão)
    historico_pontos = SessaoLog.listar_historico_por_personagem(id)
    retrato_url, retrato_do_bestiario = retrato_do_personagem(personagem)
    acesso_ate = None
    dono_id = personagem.get('id_usuario_jogador')
    usuario_logado = session.get('user_id')
    if usuario_logado and (dono_id is None or int(dono_id) != int(usuario_logado)):
        acesso_ate = AcessoTemporario.expira_de(id, usuario_logado)

    return render_template('personagem.html',
                         personagem=personagem,
                         retrato_url=retrato_url,
                         retrato_do_bestiario=retrato_do_bestiario,
                         atributos=atributos,
                         atributos_derivados=atributos_derivados,
                         vantagens=vantagens,
                         pericias=pericias_processadas,
                         inventario=itens_inventario_nao_equipados,
                         equipamentos=equipamentos,
                         inventario_efeitos=efeitos_itens,
                         peso_total=peso_total,
                         valor_total_inventario=valor_total_inventario,
                         nivel_carga=nivel_carga,
                         dinheiro_disponivel=personagem.get('dinheiro') or 0,
                         pode_equipar=pode_equipar,
                         pontos_resumo={
                             'pontos_base': pontos_base,
                             'pontos_ganhos': pontos_ganhos,
                             'pontos_gastos': pontos_gastos,
                             'pontos_disponiveis': pontos_disponiveis_ficha,  # Pontos disponíveis na ficha
                             'pontos_disponiveis_usuario': pontos_disponiveis_usuario  # Pontos disponíveis do usuário (concedidos pelo admin)
                         },
                         historico_pontos=historico_pontos,
                         magias=Magia.listar_por_personagem(id),
                         escolas_magia=Magia.ESCOLAS,
                         catalogo_magias=Acervo.listar_disponiveis('magias', personagem.get('id_campanha')) if verificar_admin() else [],
                         usuarios=Usuario.listar_todos() if verificar_admin() else [],
                         acessos_temporarios=AcessoTemporario.listar_ativos(id) if verificar_admin() else [],
                         acesso_ate=acesso_ate)

@bp.route('/api/personagem/<int:personagem_id>/biografia', methods=['PUT'])
def atualizar_biografia(personagem_id):
    """Atualiza a biografia do personagem"""
    dados = request.json
    try:
        personagem = Personagem.buscar_por_id(personagem_id)
        if not personagem:
            return jsonify({'success': False, 'message': 'Personagem não encontrado'}), 404
        
        # Atualiza apenas biografia
        query = "UPDATE personagens SET biografia = %s WHERE id = %s"
        Database.execute_query(query, (dados.get('biografia', ''), personagem_id), fetch=False)
        return jsonify({'success': True, 'message': 'Biografia atualizada!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/personagem/<int:personagem_id>/observacoes', methods=['PUT'])
def atualizar_observacoes(personagem_id):
    """Atualiza as observações do personagem"""
    dados = request.json
    try:
        query = "UPDATE personagens SET observacoes_mestre = %s WHERE id = %s"
        Database.execute_query(query, (dados.get('observacoes', ''), personagem_id), fetch=False)
        return jsonify({'success': True, 'message': 'Observações atualizadas!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/personagem/<int:id>/premium')
@exigir_login(mensagem='Faça login para acessar.', categoria='danger')
def ficha_premium(id):
    """
    Renderiza a página de visualização da ficha premium em PDF.
    O PDF é exibido diretamente no navegador usando iframe.
    """
    
    personagem = Personagem.buscar_por_id(id)
    if not personagem or _ficha_oculta(personagem) or not pode_gerenciar_personagem(personagem):
        flash('Esta ficha não está atribuída a você.', 'danger')
        return redirect(url_for('ficha.index'))
    
    response = make_response(render_template('ficha_pdf_viewer.html', personagem=personagem))
    # Headers anti-cache
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@bp.route('/personagem/<int:id>/premium/pdf')
def ficha_premium_pdf(id):
    """
    Gera e retorna PDF da ficha de personagem para visualização inline no navegador.
    Headers configurados para exibição inline (não download).
    """
    if not verificar_login():
        return jsonify({'error': 'Não autenticado'}), 401
    
    personagem = Personagem.buscar_por_id(id)
    if not personagem or _ficha_oculta(personagem) or not pode_gerenciar_personagem(personagem):
        return jsonify({'error': 'Esta ficha não está atribuída a você.'}), 403
    
    try:
        try:
            from utils.pdf_generator import gerar_ficha_pdf_personagem
        except ImportError as import_err:
            return jsonify({
                'error': f'Erro ao importar gerador de PDF: {str(import_err)}. Verifique se as dependências estão instaladas (pdfrw, reportlab, matplotlib, PyPDF2).'
            }), 500
        
        # Modo teste: apenas ST no centro (remover depois)
        modo_teste = request.args.get('teste', 'false').lower() == 'true'
        
        # Gera o PDF
        pdf_buffer = gerar_ficha_pdf_personagem(id, modo_teste=modo_teste)
        
        # Prepara resposta HTTP com headers para visualização inline
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename="ficha.pdf"'
        # Permite visualização inline no iframe
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # Headers anti-cache para garantir sempre a versão mais recente
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
        
    except FileNotFoundError as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Template PDF não encontrado: {str(e)}'}), 404
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        # Em produção, não logar trace completo, apenas erro
        if Config.DEBUG:
            print(f"ERRO ao gerar PDF: {error_trace}")
        return jsonify({'error': f'Erro ao gerar PDF: {str(e)}', 'details': error_trace.split('\n')[-5:] if Config.DEBUG else []}), 500

@bp.route('/personagem/<int:id>/premium/download')
@exigir_login(mensagem='Faça login para acessar.', categoria='danger')
def ficha_premium_download(id):
    """
    Gera e retorna PDF da ficha de personagem para download.
    Headers configurados para forçar download.
    """
    
    personagem = Personagem.buscar_por_id(id)
    if not personagem or _ficha_oculta(personagem) or not pode_gerenciar_personagem(personagem):
        flash('Esta ficha não está atribuída a você.', 'danger')
        return redirect(url_for('ficha.index'))
    
    try:
        try:
            from utils.pdf_generator import gerar_ficha_pdf_personagem
        except ImportError as import_err:
            flash(f'Erro ao importar gerador de PDF: {str(import_err)}. Verifique se as dependências estão instaladas (pdfrw, reportlab, matplotlib, PyPDF2).', 'danger')
            return redirect(url_for('ficha.ver_personagem', id=id))
        
        # Modo teste: apenas ST no centro (remover depois)
        modo_teste = request.args.get('teste', 'false').lower() == 'true'
        
        # Gera o PDF
        pdf_buffer = gerar_ficha_pdf_personagem(id, modo_teste=modo_teste)
        
        # Prepara resposta HTTP com headers para download
        nome_personagem = personagem.get('nome', 'Personagem').replace(' ', '_')
        filename = f'ficha_{nome_personagem}_{id}.pdf'
        
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except FileNotFoundError as e:
        flash(f'Template PDF não encontrado. Verifique se o arquivo static/templates/ficha_personagem_template.pdf existe.', 'danger')
        return redirect(url_for('ficha.ver_personagem', id=id))
    except Exception as e:
        flash(f'Erro ao gerar PDF: {str(e)}', 'danger')
        return redirect(url_for('ficha.ver_personagem', id=id))

@bp.route('/personagem/novo', methods=['GET', 'POST'])
@exigir_admin(mensagem='Apenas administradores podem criar personagens.', destino='ficha.index')
def novo_personagem():
    """Cria um novo personagem (apenas admin)"""
    
    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('campanhas.listar_campanhas'))

    if request.method == 'POST':
        dados = {
            'nome': request.form.get('nome'),
            'jogador_nome': request.form.get('jogador_nome'),
            'raca': request.form.get('raca'),
            'pontos_base': int(request.form.get('pontos_base', 0)),
            'pontos_desvantagens_max': int(request.form.get('pontos_desvantagens_max', 0)),
            'biografia': request.form.get('biografia'),
            'tipo': request.form.get('tipo', 'PJ'),
            'status': 'Ativo',
            'id_campanha': campanha['id']
        }
        
        # Cria o personagem
        personagem_id = Personagem.criar(dados)
        
        # Cria os atributos padrão
        ST = int(request.form.get('ST', 10))
        DX = int(request.form.get('DX', 10))
        IQ = int(request.form.get('IQ', 10))
        HT = int(request.form.get('HT', 10))
        Atributos.criar(personagem_id, ST, DX, IQ, HT)
        
        flash('Personagem criado com sucesso!', 'success')
        return redirect(url_for('ficha.ver_personagem', id=personagem_id))
    
    return render_template('novo_personagem.html')

@bp.route('/minha-ficha/criar', methods=['GET', 'POST'])
@exigir_login(mensagem='Você precisa estar logado para criar uma ficha.', categoria='danger')
def criar_minha_ficha():
    """Permite que usuários criem suas próprias fichas usando pontos disponíveis"""

    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('campanhas.listar_campanhas'))
    
    user_id = session.get('user_id')
    usuario = Usuario.buscar_por_id(user_id)
    
    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('ficha.index'))
    
    # Verifica se já tem uma ficha
    ficha_existente = Personagem.buscar_por_usuario(user_id)
    if ficha_existente:
        flash('Você já possui uma ficha. Cada usuário pode ter apenas uma ficha.', 'warning')
        return redirect(url_for('ficha.ver_personagem', id=ficha_existente['id']))
    
    pontos_disponiveis = usuario.get('pontos_disponiveis', 0) or 0
    
    if pontos_disponiveis <= 0:
        flash('Você não possui pontos disponíveis para criar uma ficha. Entre em contato com o administrador.', 'danger')
        return redirect(url_for('ficha.index'))
    
    if request.method == 'POST':
        try:
            pontos_base = int(request.form.get('pontos_base', pontos_disponiveis))
            
            # Valida que não está usando mais pontos do que tem disponível
            if pontos_base > pontos_disponiveis:
                flash(f'Você não pode usar mais de {pontos_disponiveis} pontos. Você possui apenas {pontos_disponiveis} pontos disponíveis.', 'danger')
                return redirect(url_for('ficha.criar_minha_ficha'))
            
            # Prepara raca_id e classe_id
            raca_id_final = None
            classe_id_final = None
            raca_id_str = request.form.get('raca_id', '').strip()
            classe_id_str = request.form.get('classe_id', '').strip()
            
            if raca_id_str:
                try:
                    raca_id_final = int(raca_id_str)
                except:
                    raca_id_final = None
            
            if classe_id_str:
                try:
                    classe_id_final = int(classe_id_str)
                except:
                    classe_id_final = None

            if raca_id_final and not pertence_a_campanha_ativa(Raca.buscar_por_id(raca_id_final)):
                raca_id_final = None
            if classe_id_final and not pertence_a_campanha_ativa(Classe.buscar_por_id(classe_id_final)):
                classe_id_final = None
            
            dados = {
                'nome': request.form.get('nome'),
                'jogador_nome': usuario.get('nome_completo') or usuario.get('username'),
                'raca': request.form.get('raca', 'Humano'),
                'pontos_base': pontos_base,
                'pontos_desvantagens_max': int(request.form.get('pontos_desvantagens_max', -50)),
                'biografia': request.form.get('biografia', ''),
                'tipo': 'PJ',
                'status': 'Ativo',
                'id_usuario_jogador': user_id,
                'raca_id': raca_id_final,
                'classe_id': classe_id_final,
                'id_campanha': campanha['id']
            }
            
            # Cria o personagem
            personagem_id = Personagem.criar(dados)
            
            # Busca informações da raça e classe selecionadas
            bonus_total = {
                'ST': 0, 'DX': 0, 'IQ': 0, 'HT': 0,
                'PV_extra': 0, 'PF_extra': 0, 'percepcao_extra': 0, 'vontade_extra': 0
            }
            custo_total_raca_classe = 0
            vantagens_automaticas_ids = []
            pericias_automaticas_ids = []
            
            # Processa raça
            if raca_id_final:
                try:
                    raca = Raca.buscar_por_id(raca_id_final)
                    if raca:
                        bonus_raca = Raca.obter_bonus(raca_id_final)
                        bonus_total['ST'] += bonus_raca.get('bonus_st', 0) or 0
                        bonus_total['DX'] += bonus_raca.get('bonus_dx', 0) or 0
                        bonus_total['IQ'] += bonus_raca.get('bonus_iq', 0) or 0
                        bonus_total['HT'] += bonus_raca.get('bonus_ht', 0) or 0
                        bonus_total['PV_extra'] += bonus_raca.get('bonus_pv_extra', 0) or 0
                        bonus_total['PF_extra'] += bonus_raca.get('bonus_pf_extra', 0) or 0
                        bonus_total['percepcao_extra'] += bonus_raca.get('bonus_percepcao_extra', 0) or 0
                        bonus_total['vontade_extra'] += bonus_raca.get('bonus_vontade_extra', 0) or 0
                        custo_total_raca_classe += bonus_raca.get('custo_em_pontos', 0) or 0
                        
                        # Processa vantagens automáticas
                        if raca.get('vantagens_automaticas'):
                            try:
                                import json
                                vantagens_ids = json.loads(raca['vantagens_automaticas'])
                                if isinstance(vantagens_ids, list):
                                    vantagens_automaticas_ids.extend(vantagens_ids)
                            except:
                                pass
                        
                        # Processa perícias automáticas
                        if raca.get('pericias_automaticas'):
                            try:
                                import json
                                pericias_ids = json.loads(raca['pericias_automaticas'])
                                if isinstance(pericias_ids, list):
                                    pericias_automaticas_ids.extend(pericias_ids)
                            except:
                                pass
                except:
                    pass
            
            # Processa classe
            if classe_id_final:
                try:
                    classe = Classe.buscar_por_id(classe_id_final)
                    if classe:
                        bonus_classe = Classe.obter_bonus(classe_id_final)
                        bonus_total['ST'] += bonus_classe.get('bonus_st', 0) or 0
                        bonus_total['DX'] += bonus_classe.get('bonus_dx', 0) or 0
                        bonus_total['IQ'] += bonus_classe.get('bonus_iq', 0) or 0
                        bonus_total['HT'] += bonus_classe.get('bonus_ht', 0) or 0
                        bonus_total['PV_extra'] += bonus_classe.get('bonus_pv_extra', 0) or 0
                        bonus_total['PF_extra'] += bonus_classe.get('bonus_pf_extra', 0) or 0
                        bonus_total['percepcao_extra'] += bonus_classe.get('bonus_percepcao_extra', 0) or 0
                        bonus_total['vontade_extra'] += bonus_classe.get('bonus_vontade_extra', 0) or 0
                        custo_total_raca_classe += bonus_classe.get('custo_em_pontos', 0) or 0
                        
                        # Processa vantagens automáticas
                        if classe.get('vantagens_automaticas'):
                            try:
                                import json
                                vantagens_ids = json.loads(classe['vantagens_automaticas'])
                                if isinstance(vantagens_ids, list):
                                    vantagens_automaticas_ids.extend(vantagens_ids)
                            except:
                                pass
                        
                        # Processa perícias automáticas
                        if classe.get('pericias_automaticas'):
                            try:
                                import json
                                pericias_ids = json.loads(classe['pericias_automaticas'])
                                if isinstance(pericias_ids, list):
                                    pericias_automaticas_ids.extend(pericias_ids)
                            except:
                                pass
                except:
                    pass
            
            # Valida custo total (custo raça/classe não pode exceder pontos disponíveis)
            # O custo total é apenas a soma dos custos de raça e classe
            # Os pontos_base são os pontos que o usuário tem para gastar na ficha
            if custo_total_raca_classe > pontos_disponiveis:
                flash(f'❌ Pontos insuficientes!\n\nVocê tem: {pontos_disponiveis} pontos\nCusto total: {custo_total_raca_classe} pontos (raça/classe)\n\nFaltam: {custo_total_raca_classe - pontos_disponiveis} pontos\n\nEscolha uma raça/classe com menor custo ou peça mais pontos ao administrador.', 'danger')
                return redirect(url_for('ficha.criar_minha_ficha'))
            
            # Cria os atributos com bônus aplicados
            ST = int(request.form.get('ST', 10)) + bonus_total['ST']
            DX = int(request.form.get('DX', 10)) + bonus_total['DX']
            IQ = int(request.form.get('IQ', 10)) + bonus_total['IQ']
            HT = int(request.form.get('HT', 10)) + bonus_total['HT']
            Atributos.criar(personagem_id, ST, DX, IQ, HT,
                          PV_extra=bonus_total['PV_extra'],
                          PF_extra=bonus_total['PF_extra'],
                          percepcao_extra=bonus_total['percepcao_extra'],
                          vontade_extra=bonus_total['vontade_extra'])
            
            # Adiciona vantagens automáticas
            from models import VantagemDesvantagemCatalogo
            for vantagem_id in vantagens_automaticas_ids:
                try:
                    vantagem_catalogo = (
                        Acervo.registro_efetivo('vantagens', campanha['id'], vantagem_id)
                        or VantagemDesvantagemCatalogo.buscar_por_id(vantagem_id)
                    )
                    if vantagem_catalogo:
                        VantagemDesvantagem.criar(
                            personagem_id,
                            vantagem_catalogo['nome'],
                            vantagem_catalogo.get('custo_base', 0),
                            f"Concedida automaticamente pela raça/classe"
                        )
                except Exception as e:
                    print(f"Erro ao adicionar vantagem automática {vantagem_id}: {str(e)}")
            
            # Adiciona perícias automáticas
            from models import PericiaCatalogo
            for pericia_id in pericias_automaticas_ids:
                try:
                    pericia_catalogo = (
                        Acervo.registro_efetivo('pericias', campanha['id'], pericia_id)
                        or PericiaCatalogo.buscar_por_id(pericia_id)
                    )
                    if pericia_catalogo:
                        Pericia.criar(
                            personagem_id,
                            pericia_catalogo['nome'],
                            pericia_catalogo['atributo_base'],
                            pericia_catalogo['dificuldade'],
                            0  # 0 pontos investidos (concedida automaticamente)
                        )
                except Exception as e:
                    print(f"Erro ao adicionar perícia automática {pericia_id}: {str(e)}")
            
            # Recalcula pontos gastos (inclui vantagens/perícias automáticas)
            Personagem.recalcular_pontos_gastos(personagem_id)
            
            # Deduz apenas o custo da raça/classe dos pontos disponíveis do usuário
            # Os pontos_base são os pontos que o usuário tem para gastar na ficha (atributos, vantagens, etc.)
            # O custo da raça/classe é um custo adicional que deve ser deduzido
            if custo_total_raca_classe > 0:
                Usuario.remover_pontos(user_id, custo_total_raca_classe)
                mensagem = f'Ficha criada com sucesso! {custo_total_raca_classe} pontos foram deduzidos para raça/classe. Você tem {pontos_base} pontos para gastar na ficha.'
            else:
                mensagem = f'Ficha criada com sucesso! Você tem {pontos_base} pontos para gastar na ficha.'
            flash(mensagem, 'success')
            return redirect(url_for('ficha.ver_personagem', id=personagem_id))
        except Exception as e:
            flash(f'Erro ao criar ficha: {str(e)}', 'danger')
    
    # Carrega raças e classes para o formulário
    racas = Raca.listar_por_campanha(campanha['id'])
    classes = Classe.listar_por_campanha(campanha['id'])
    
    return render_template('criar_minha_ficha.html', 
                         pontos_disponiveis=pontos_disponiveis,
                         racas=racas,
                         classes=classes)

@bp.route('/minha-ficha')
@exigir_login(mensagem='Você precisa estar logado para ver sua ficha.', categoria='danger')
def minha_ficha():
    """Abre a ficha do usuário logado na campanha ativa, ou lista as fichas se ele tiver mais de uma"""

    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('campanhas.listar_campanhas'))

    fichas = Personagem.listar_por_usuario(session.get('user_id'), campanha['id'])
    if not fichas:
        flash('Você ainda não possui uma ficha. Crie uma agora!', 'info')
        return redirect(url_for('ficha.criar_minha_ficha'))
    if len(fichas) == 1:
        return redirect(url_for('ficha.ver_personagem', id=fichas[0]['id']))
    return render_template('minhas_fichas.html', fichas=fichas)

@bp.route('/minha-ficha/deletar', methods=['POST'])
@exigir_login(mensagem='Você precisa estar logado para deletar sua ficha.', categoria='danger')
def deletar_minha_ficha():
    """Deleta a ficha do usuário e retorna os pontos"""
    
    user_id = session.get('user_id')
    ficha = Personagem.buscar_por_id(request.form.get('personagem_id', type=int) or 0)
    
    if not ficha:
        flash('Você não possui uma ficha para deletar.', 'warning')
        return redirect(url_for('ficha.index'))
    
    # Verifica se é realmente a ficha do usuário
    if ficha.get('id_usuario_jogador') != user_id:
        flash('Você não tem permissão para deletar esta ficha.', 'danger')
        return redirect(url_for('ficha.index'))
    
    try:
        # Calcula pontos a retornar (apenas o custo da raça/classe)
        # Os pontos_base não foram deduzidos, então não precisam ser retornados
        
        # Busca custo da raça
        custo_raca = 0
        if ficha.get('raca_id'):
            try:
                raca = Raca.buscar_por_id(ficha['raca_id'])
                if raca:
                    custo_raca = raca.get('custo_em_pontos', 0) or 0
            except:
                pass
        
        # Busca custo da classe
        custo_classe = 0
        if ficha.get('classe_id'):
            try:
                classe = Classe.buscar_por_id(ficha['classe_id'])
                if classe:
                    custo_classe = classe.get('custo_em_pontos', 0) or 0
            except:
                pass
        
        pontos_retornar = custo_raca + custo_classe
        
        # Retorna os pontos ao usuário
        Usuario.adicionar_pontos(user_id, pontos_retornar)
        
        # Deleta o personagem (cascade deleta atributos, vantagens, perícias, etc)
        remover_retratos(ficha['id'])
        Personagem.deletar(ficha['id'])
        
        flash(f'Ficha deletada com sucesso! {pontos_retornar} pontos foram retornados à sua conta.', 'success')
        return redirect(url_for('ficha.criar_minha_ficha'))
    except Exception as e:
        flash(f'Erro ao deletar ficha: {str(e)}', 'danger')
        return redirect(url_for('ficha.ver_personagem', id=ficha['id']))


def _ficha_oculta(personagem: dict) -> bool:
    """Ficha de criatura do bestiário que o mestre ainda não revelou aos jogadores."""
    if not personagem or verificar_admin() or not personagem.get('id_campanha'):
        return False
    if personagem['id'] not in Bestiario.fichas_bloqueadas(personagem['id_campanha']):
        return False
    try:
        dono = personagem.get('id_usuario_jogador')
        if dono is not None and int(dono) == int(session.get('user_id') or 0):
            return False
    except (TypeError, ValueError):
        pass
    return not AcessoTemporario.esta_ativo(personagem['id'], session.get('user_id'))

# ==========================================
# Rotas - Upload de Imagens
# ==========================================
