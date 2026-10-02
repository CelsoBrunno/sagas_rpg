# ==========================================
# Sistema de Campanha GURPS - Flask App
# ==========================================

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file, make_response
from database import Database
from models import (
    Personagem, Atributos, VantagemDesvantagem, Pericia,
    Campanha, Usuario, Local, NPC, Mapa, Imagem, Inventario, SessaoLog, PericiaCatalogo,
    VantagemDesvantagemCatalogo, ItemCatalogo, Equipamento, Raca, Classe, Bestiario
)
from config import Config
import os
from werkzeug.utils import secure_filename
from decimal import Decimal
from utils.item_effects import enriquecer_inventario
from utils.acesso import (
    verificar_admin, verificar_login, campanha_da_sessao,
    exigir_campanha, pertence_a_campanha_ativa
)
from utils.uploads import allowed_file
from routes.bestiario import bp as bestiario_bp

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Configuração para recarregar templates automaticamente em desenvolvimento
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

# Configuração de upload de imagens
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Criar pasta de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Inicializa o pool de conexões
Database.init_app(app)

app.register_blueprint(bestiario_bp)

# ==========================================
# Rotas Principais
# ==========================================

@app.route('/')
def index():
    """Página inicial - lista de personagens"""
    if not verificar_login():
        flash('Faça login para acessar o sistema.', 'info')
        return redirect(url_for('login'))
    
    campanha = campanha_da_sessao()
    personagens = Personagem.listar_por_campanha(campanha['id']) if campanha else []
    if campanha and not verificar_admin():
        ocultas = Bestiario.fichas_bloqueadas(campanha['id'])
        personagens = [p for p in personagens if p['id'] not in ocultas]
    return render_template('index.html', personagens=personagens, sem_campanha=campanha is None)

@app.route('/personagem/<int:id>')
def ver_personagem(id):
    """Visualiza uma ficha de personagem completa"""
    personagem = Personagem.buscar_por_id(id)
    
    if not personagem:
        flash('Personagem não encontrado.', 'danger')
        return redirect(url_for('index'))

    if personagem.get('id_campanha') and not pertence_a_campanha_ativa(personagem):
        flash('Esse personagem pertence a outra campanha.', 'danger')
        return redirect(url_for('index'))

    if _ficha_oculta(personagem):
        flash('Esta criatura ainda não foi revelada.', 'info')
        return redirect(url_for('bestiario.listar_bestiario'))

    pode_equipar = _usuario_pode_gerenciar_personagem(personagem)
    
    atributos = Atributos.buscar_por_personagem(id)
    vantagens = VantagemDesvantagem.listar_por_personagem(id)
    atributos_derivados = Atributos.calcular_atributos_derivados(atributos, vantagens) if atributos else {}
    # Campos adicionais solicitados
    if atributos:
        # Percepção e Vontade já são calculados em calcular_atributos_derivados
        if 'percepcao' not in atributos_derivados:
            atributos_derivados['percepcao'] = atributos['IQ']
        if 'vontade' not in atributos_derivados:
            atributos_derivados['vontade'] = atributos['IQ']
        atributos_derivados['deslocamento'] = int(atributos_derivados.get('velocidade_basica', 0))
        # Bases simplificadas
        # Aparar e Bloqueio com bônus de vantagens
        bonus_aparar = atributos_derivados.get('bonus_aparar', 0)
        bonus_bloqueio = atributos_derivados.get('bonus_bloqueio', 0)
        atributos_derivados['aparar'] = int(atributos['DX'] / 2) + Config.APARAR_BASE + bonus_aparar
        atributos_derivados['bloqueio'] = Config.BLOQUEIO_BASE + bonus_bloqueio
    
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
        from models import Usuario
        pontos_disponiveis_usuario = Usuario.get_pontos_disponiveis(personagem['id_usuario_jogador'])

    # Histórico de evolução (pontos por sessão)
    historico_pontos = SessaoLog.listar_historico_por_personagem(id)

    return render_template('personagem.html',
                         personagem=personagem,
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
                         historico_pontos=historico_pontos)

@app.route('/api/personagem/<int:personagem_id>/biografia', methods=['PUT'])
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

@app.route('/api/personagem/<int:personagem_id>/observacoes', methods=['PUT'])
def atualizar_observacoes(personagem_id):
    """Atualiza as observações do personagem"""
    dados = request.json
    try:
        query = "UPDATE personagens SET observacoes_mestre = %s WHERE id = %s"
        Database.execute_query(query, (dados.get('observacoes', ''), personagem_id), fetch=False)
        return jsonify({'success': True, 'message': 'Observações atualizadas!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/personagem/<int:id>/premium')
def ficha_premium(id):
    """
    Renderiza a página de visualização da ficha premium em PDF.
    O PDF é exibido diretamente no navegador usando iframe.
    """
    if not verificar_login():
        flash('Faça login para acessar.', 'danger')
        return redirect(url_for('login'))
    
    personagem = Personagem.buscar_por_id(id)
    if not personagem or _ficha_oculta(personagem):
        flash('Personagem não encontrado.', 'danger')
        return redirect(url_for('index'))
    
    response = make_response(render_template('ficha_pdf_viewer.html', personagem=personagem))
    # Headers anti-cache
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/personagem/<int:id>/premium/pdf')
def ficha_premium_pdf(id):
    """
    Gera e retorna PDF da ficha de personagem para visualização inline no navegador.
    Headers configurados para exibição inline (não download).
    """
    if not verificar_login():
        return jsonify({'error': 'Não autenticado'}), 401
    
    personagem = Personagem.buscar_por_id(id)
    if not personagem or _ficha_oculta(personagem):
        return jsonify({'error': 'Personagem não encontrado'}), 404
    
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

@app.route('/personagem/<int:id>/premium/download')
def ficha_premium_download(id):
    """
    Gera e retorna PDF da ficha de personagem para download.
    Headers configurados para forçar download.
    """
    if not verificar_login():
        flash('Faça login para acessar.', 'danger')
        return redirect(url_for('login'))
    
    personagem = Personagem.buscar_por_id(id)
    if not personagem or _ficha_oculta(personagem):
        flash('Personagem não encontrado.', 'danger')
        return redirect(url_for('index'))
    
    try:
        try:
            from utils.pdf_generator import gerar_ficha_pdf_personagem
        except ImportError as import_err:
            flash(f'Erro ao importar gerador de PDF: {str(import_err)}. Verifique se as dependências estão instaladas (pdfrw, reportlab, matplotlib, PyPDF2).', 'danger')
            return redirect(url_for('ver_personagem', id=id))
        
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
        return redirect(url_for('ver_personagem', id=id))
    except Exception as e:
        flash(f'Erro ao gerar PDF: {str(e)}', 'danger')
        return redirect(url_for('ver_personagem', id=id))

@app.route('/personagem/novo', methods=['GET', 'POST'])
def novo_personagem():
    """Cria um novo personagem (apenas admin)"""
    if not verificar_admin():
        flash('Apenas administradores podem criar personagens.', 'danger')
        return redirect(url_for('index'))
    
    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('listar_campanhas'))

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
        return redirect(url_for('ver_personagem', id=personagem_id))
    
    return render_template('novo_personagem.html')

@app.route('/minha-ficha/criar', methods=['GET', 'POST'])
def criar_minha_ficha():
    """Permite que usuários criem suas próprias fichas usando pontos disponíveis"""
    if not verificar_login():
        flash('Você precisa estar logado para criar uma ficha.', 'danger')
        return redirect(url_for('login'))

    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('listar_campanhas'))
    
    user_id = session.get('user_id')
    usuario = Usuario.buscar_por_id(user_id)
    
    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('index'))
    
    # Verifica se já tem uma ficha
    ficha_existente = Personagem.buscar_por_usuario(user_id)
    if ficha_existente:
        flash('Você já possui uma ficha. Cada usuário pode ter apenas uma ficha.', 'warning')
        return redirect(url_for('ver_personagem', id=ficha_existente['id']))
    
    pontos_disponiveis = usuario.get('pontos_disponiveis', 0) or 0
    
    if pontos_disponiveis <= 0:
        flash('Você não possui pontos disponíveis para criar uma ficha. Entre em contato com o administrador.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            pontos_base = int(request.form.get('pontos_base', pontos_disponiveis))
            
            # Valida que não está usando mais pontos do que tem disponível
            if pontos_base > pontos_disponiveis:
                flash(f'Você não pode usar mais de {pontos_disponiveis} pontos. Você possui apenas {pontos_disponiveis} pontos disponíveis.', 'danger')
                return redirect(url_for('criar_minha_ficha'))
            
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
                return redirect(url_for('criar_minha_ficha'))
            
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
                    vantagem_catalogo = VantagemDesvantagemCatalogo.buscar_por_id(vantagem_id)
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
                    pericia_catalogo = PericiaCatalogo.buscar_por_id(pericia_id)
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
            return redirect(url_for('ver_personagem', id=personagem_id))
        except Exception as e:
            flash(f'Erro ao criar ficha: {str(e)}', 'danger')
    
    # Carrega raças e classes para o formulário
    racas = Raca.listar_por_campanha(campanha['id'])
    classes = Classe.listar_por_campanha(campanha['id'])
    
    return render_template('criar_minha_ficha.html', 
                         pontos_disponiveis=pontos_disponiveis,
                         racas=racas,
                         classes=classes)

@app.route('/minha-ficha')
def minha_ficha():
    """Redireciona para a ficha do usuário logado"""
    if not verificar_login():
        flash('Você precisa estar logado para ver sua ficha.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    ficha = Personagem.buscar_por_usuario(user_id)
    
    if not ficha:
        flash('Você ainda não possui uma ficha. Crie uma agora!', 'info')
        return redirect(url_for('criar_minha_ficha'))
    
    return redirect(url_for('ver_personagem', id=ficha['id']))

@app.route('/minha-ficha/deletar', methods=['POST'])
def deletar_minha_ficha():
    """Deleta a ficha do usuário e retorna os pontos"""
    if not verificar_login():
        flash('Você precisa estar logado para deletar sua ficha.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    ficha = Personagem.buscar_por_usuario(user_id)
    
    if not ficha:
        flash('Você não possui uma ficha para deletar.', 'warning')
        return redirect(url_for('index'))
    
    # Verifica se é realmente a ficha do usuário
    if ficha.get('id_usuario_jogador') != user_id:
        flash('Você não tem permissão para deletar esta ficha.', 'danger')
        return redirect(url_for('index'))
    
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
        Personagem.deletar(ficha['id'])
        
        flash(f'Ficha deletada com sucesso! {pontos_retornar} pontos foram retornados à sua conta.', 'success')
        return redirect(url_for('criar_minha_ficha'))
    except Exception as e:
        flash(f'Erro ao deletar ficha: {str(e)}', 'danger')
        return redirect(url_for('ver_personagem', id=ficha['id']))

# ==========================================
# APIs - Vantagens e Desvantagens
# ==========================================

@app.route('/api/personagem/<int:personagem_id>/vantagens', methods=['POST'])
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

@app.route('/api/vantagens/<int:vd_id>', methods=['DELETE'])
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

@app.route('/api/personagem/<int:personagem_id>/pericias', methods=['POST'])
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

@app.route('/api/pericias/<int:pericia_id>', methods=['PUT'])
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

@app.route('/api/pericias/<int:pericia_id>', methods=['DELETE'])
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

@app.route('/api/personagem/<int:personagem_id>/atributos', methods=['PUT'])
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

@app.route('/api/rolar/<int:alvo>', methods=['POST'])
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

@app.route('/ultimas-rolagens')
def ultimas_rolagens():
    if not verificar_login():
        return redirect(url_for('login'))
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

# ==========================================
# Rota para Health Check
# ==========================================

@app.route('/health')
def health():
    """Verifica o status da aplicação"""
    return jsonify({
        'status': 'healthy',
        'database': 'connected' if Database._connection_pool else 'not_connected'
    })

# ==========================================
# Rotas - Locais (Módulo 2)
# ==========================================

@app.route('/locais')
def listar_locais():
    """Lista todos os locais"""
    if not verificar_login():
        return redirect(url_for('login'))
    
    campanha = campanha_da_sessao()
    locais = Local.listar_por_campanha(campanha['id']) if campanha else []
    return render_template('locais_index.html', locais=locais, sem_campanha=campanha is None)

@app.route('/local/<int:id>')
def ver_local(id):
    """Visualiza detalhes de um local"""
    if not verificar_login():
        return redirect(url_for('login'))

    local = Local.buscar_por_id(id)
    if not local or not pertence_a_campanha_ativa(local):
        flash('Local não encontrado nesta campanha.', 'danger')
        return redirect(url_for('listar_locais'))
    
    # Debug: verificar imagem
    if Config.DEBUG and local.get('imagem_principal_url'):
        print(f"DEBUG: Local {id} - imagem_principal_url: {local.get('imagem_principal_url')}")
    
    # Busca NPCs presentes neste local
    npcs = NPC.listar_por_local(id) or []

    # Notas de mestre e lore completa ficam fora da página do jogador
    if not verificar_admin():
        local = dict(local)
        local['descricao_mestre'] = None
        npcs_publicos = []
        for npc in npcs:
            npc_publico = dict(npc)
            npc_publico['descricao_completa'] = None
            npcs_publicos.append(npc_publico)
        npcs = npcs_publicos
    
    # Busca mapas associados a este local
    mapas = Mapa.listar_por_local(id)
    
    return render_template('local_detalhe.html',
                         local=local,
                         npcs=npcs,
                         mapas=mapas)

@app.route('/local/novo', methods=['GET', 'POST'])
def novo_local():
    """Cria um novo local"""
    if not verificar_admin():
        flash('Apenas administradores podem criar locais.', 'danger')
        return redirect(url_for('listar_locais'))

    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('listar_campanhas'))
    
    if request.method == 'POST':
        imagem_url = None
        
        # Processa upload de imagem
        if 'arquivo' in request.files and request.files['arquivo'].filename:
            file = request.files['arquivo']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"local_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                imagem_url = f"/static/uploads/{filename}"
            else:
                flash('Tipo de arquivo inválido. Use PNG, JPG, JPEG, GIF ou WEBP.', 'danger')
                return render_template('local_novo.html')
        
        dados = {
            'nome': request.form.get('nome'),
            'tipo': request.form.get('tipo'),
            'descricao_publica': request.form.get('descricao_publica'),
            'descricao_mestre': request.form.get('descricao_mestre'),
            'imagem_principal_url': imagem_url,
            'id_campanha': campanha['id']
        }
        
        if not dados['nome']:
            flash('Nome é obrigatório.', 'danger')
            return render_template('local_novo.html')
        
        try:
            local_id = Local.criar(dados)
            flash('Local criado com sucesso!', 'success')
            return redirect(url_for('ver_local', id=local_id))
        except Exception as e:
            flash(f'Erro ao criar local: {str(e)}', 'danger')
    
    return render_template('local_novo.html')

@app.route('/local/<int:id>/editar', methods=['GET', 'POST'])
def editar_local(id):
    """Edita um local existente"""
    if not verificar_admin():
        flash('Apenas administradores podem editar locais.', 'danger')
        return redirect(url_for('listar_locais'))
    
    local = Local.buscar_por_id(id)
    if not local or not pertence_a_campanha_ativa(local):
        flash('Local não encontrado nesta campanha.', 'danger')
        return redirect(url_for('listar_locais'))
    
    if request.method == 'POST':
        imagem_url = local.get('imagem_principal_url')  # Mantém a imagem atual por padrão
        
        # Verifica se há novo upload
        if 'arquivo' in request.files and request.files['arquivo'].filename:
            file = request.files['arquivo']
            if file and allowed_file(file.filename):
                # Remove a imagem antiga se existir
                if local.get('imagem_principal_url') and local['imagem_principal_url'].startswith('/static/uploads/'):
                    arquivo_antigo = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                                  local['imagem_principal_url'].lstrip('/'))
                    if os.path.exists(arquivo_antigo):
                        try:
                            os.remove(arquivo_antigo)
                        except:
                            pass
                
                filename = secure_filename(f"local_{id}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                imagem_url = f"/static/uploads/{filename}"
            else:
                flash('Tipo de arquivo inválido. Use PNG, JPG, JPEG, GIF ou WEBP.', 'danger')
                return render_template('local_editar.html', local=local)
        
        dados = {
            'nome': request.form.get('nome'),
            'tipo': request.form.get('tipo'),
            'descricao_publica': request.form.get('descricao_publica'),
            'descricao_mestre': request.form.get('descricao_mestre'),
            'imagem_principal_url': imagem_url
        }
        
        if not dados['nome']:
            flash('Nome é obrigatório.', 'danger')
            return render_template('local_editar.html', local=local)
        
        try:
            Local.atualizar(id, dados)
            flash('Local atualizado com sucesso!', 'success')
            return redirect(url_for('ver_local', id=id))
        except Exception as e:
            flash(f'Erro ao atualizar local: {str(e)}', 'danger')
    
    return render_template('local_editar.html', local=local)

@app.route('/local/<int:id>/deletar', methods=['POST'])
def deletar_local(id):
    """Deleta um local"""
    if not verificar_admin():
        flash('Apenas administradores podem deletar locais.', 'danger')
        return redirect(url_for('listar_locais'))
    
    local = Local.buscar_por_id(id)
    if not local or not pertence_a_campanha_ativa(local):
        flash('Local não encontrado nesta campanha.', 'danger')
        return redirect(url_for('listar_locais'))
    
    try:
        # Tenta deletar o arquivo físico se existir
        if local.get('imagem_principal_url') and local['imagem_principal_url'].startswith('/static/uploads/'):
            arquivo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                      local['imagem_principal_url'].lstrip('/'))
            if os.path.exists(arquivo_path):
                try:
                    os.remove(arquivo_path)
                except:
                    pass  # Ignora erros ao deletar arquivo
        
        Local.deletar(id)
        flash('Local deletado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao deletar local: {str(e)}', 'danger')
    
    return redirect(url_for('listar_locais'))

# ==========================================
# Rotas - NPCs (Módulo 3)
# ==========================================

@app.route('/npcs')
def listar_npcs():
    """Lista todos os NPCs"""
    if not verificar_login():
        return redirect(url_for('login'))
    
    campanha = campanha_da_sessao()
    npcs = NPC.listar_por_campanha(campanha['id']) if campanha else []
    return render_template('npcs_index.html', npcs=npcs, sem_campanha=campanha is None)

@app.route('/npc/<int:id>')
def ver_npc(id):
    """Visualiza detalhes de um NPC"""
    if not verificar_login():
        return redirect(url_for('login'))

    npc = NPC.buscar_por_id(id)
    if not npc or not pertence_a_campanha_ativa(npc):
        flash('NPC não encontrado nesta campanha.', 'danger')
        return redirect(url_for('listar_npcs'))

    if not verificar_admin():
        npc = dict(npc)
        npc['descricao_completa'] = None
    
    return render_template('npc_detalhe.html', npc=npc)

@app.route('/npc/novo', methods=['GET', 'POST'])
def novo_npc():
    """Cria um novo NPC"""
    if not verificar_admin():
        flash('Apenas administradores podem criar NPCs.', 'danger')
        return redirect(url_for('listar_npcs'))

    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('listar_campanhas'))
    
    if request.method == 'POST':
        imagem_url = None
        
        # Processa upload de imagem
        if 'arquivo' in request.files and request.files['arquivo'].filename:
            file = request.files['arquivo']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"npc_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                imagem_url = f"/static/uploads/{filename}"
            else:
                flash('Tipo de arquivo inválido. Use PNG, JPG, JPEG, GIF ou WEBP.', 'danger')
                locais = Local.listar_por_campanha(campanha['id'])
                personagens = Personagem.listar_por_campanha(campanha['id'])
                return render_template('npc_novo.html', locais=locais, personagens=personagens)
        
        dados = {
            'nome': request.form.get('nome'),
            'status': request.form.get('status', 'Vivo'),
            'descricao_breve': request.form.get('descricao_breve'),
            'descricao_completa': request.form.get('descricao_completa'),
            'imagem_url': imagem_url,
            'local_atual_id': request.form.get('local_atual_id') or None,
            'ficha_personagem_id': request.form.get('ficha_personagem_id') or None,
            'id_campanha': campanha['id']
        }
        
        if dados['local_atual_id']:
            dados['local_atual_id'] = int(dados['local_atual_id'])
        if dados['ficha_personagem_id']:
            dados['ficha_personagem_id'] = int(dados['ficha_personagem_id'])
        
        if not dados['nome']:
            flash('Nome é obrigatório.', 'danger')
            locais = Local.listar_por_campanha(campanha['id'])
            personagens = Personagem.listar_por_campanha(campanha['id'])
            return render_template('npc_novo.html', locais=locais, personagens=personagens)
        
        try:
            npc_id = NPC.criar(dados)
            flash('NPC criado com sucesso!', 'success')
            return redirect(url_for('ver_npc', id=npc_id))
        except Exception as e:
            flash(f'Erro ao criar NPC: {str(e)}', 'danger')
    
    locais = Local.listar_por_campanha(campanha['id'])
    personagens = Personagem.listar_por_campanha(campanha['id'])
    return render_template('npc_novo.html', locais=locais, personagens=personagens)

@app.route('/npc/<int:id>/editar', methods=['GET', 'POST'])
def editar_npc(id):
    """Edita um NPC existente"""
    if not verificar_admin():
        flash('Apenas administradores podem editar NPCs.', 'danger')
        return redirect(url_for('listar_npcs'))
    
    npc = NPC.buscar_por_id(id)
    if not npc or not pertence_a_campanha_ativa(npc):
        flash('NPC não encontrado nesta campanha.', 'danger')
        return redirect(url_for('listar_npcs'))

    campanha = campanha_da_sessao()
    
    if request.method == 'POST':
        imagem_url = npc.get('imagem_url')  # Mantém a imagem atual por padrão
        
        # Verifica se há novo upload
        if 'arquivo' in request.files and request.files['arquivo'].filename:
            file = request.files['arquivo']
            if file and allowed_file(file.filename):
                # Remove a imagem antiga se existir
                if npc.get('imagem_url') and npc['imagem_url'].startswith('/static/uploads/'):
                    arquivo_antigo = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                                 npc['imagem_url'].lstrip('/'))
                    if os.path.exists(arquivo_antigo):
                        try:
                            os.remove(arquivo_antigo)
                        except:
                            pass
                
                filename = secure_filename(f"npc_{id}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                imagem_url = f"/static/uploads/{filename}"
            else:
                flash('Tipo de arquivo inválido. Use PNG, JPG, JPEG, GIF ou WEBP.', 'danger')
                locais = Local.listar_por_campanha(session.get('campanha_id'))
                personagens = Personagem.listar_por_campanha(session.get('campanha_id'))
                return render_template('npc_editar.html', npc=npc, locais=locais, personagens=personagens)
        
        dados = {
            'nome': request.form.get('nome'),
            'status': request.form.get('status', 'Vivo'),
            'descricao_breve': request.form.get('descricao_breve'),
            'descricao_completa': request.form.get('descricao_completa'),
            'imagem_url': imagem_url,
            'local_atual_id': request.form.get('local_atual_id') or None,
            'ficha_personagem_id': request.form.get('ficha_personagem_id') or None
        }
        
        if dados['local_atual_id']:
            dados['local_atual_id'] = int(dados['local_atual_id'])
        if dados['ficha_personagem_id']:
            dados['ficha_personagem_id'] = int(dados['ficha_personagem_id'])
        
        if not dados['nome']:
            flash('Nome é obrigatório.', 'danger')
            locais = Local.listar_por_campanha(session.get('campanha_id'))
            personagens = Personagem.listar_por_campanha(session.get('campanha_id'))
            return render_template('npc_editar.html', npc=npc, locais=locais, personagens=personagens)
        
        try:
            NPC.atualizar(id, dados)
            flash('NPC atualizado com sucesso!', 'success')
            return redirect(url_for('ver_npc', id=id))
        except Exception as e:
            flash(f'Erro ao atualizar NPC: {str(e)}', 'danger')
    
    locais = Local.listar_por_campanha(session.get('campanha_id'))
    personagens = Personagem.listar_por_campanha(session.get('campanha_id'))
    return render_template('npc_editar.html', npc=npc, locais=locais, personagens=personagens)

@app.route('/npc/<int:id>/deletar', methods=['POST'])
def deletar_npc(id):
    """Deleta um NPC"""
    if not verificar_admin():
        flash('Apenas administradores podem deletar NPCs.', 'danger')
        return redirect(url_for('listar_npcs'))
    
    npc = NPC.buscar_por_id(id)
    if not npc or not pertence_a_campanha_ativa(npc):
        flash('NPC não encontrado nesta campanha.', 'danger')
        return redirect(url_for('listar_npcs'))
    
    try:
        # Tenta deletar o arquivo físico se existir
        if npc.get('imagem_url') and npc['imagem_url'].startswith('/static/uploads/'):
            arquivo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                      npc['imagem_url'].lstrip('/'))
            if os.path.exists(arquivo_path):
                try:
                    os.remove(arquivo_path)
                except:
                    pass  # Ignora erros ao deletar arquivo
        
        NPC.deletar(id)
        flash('NPC deletado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao deletar NPC: {str(e)}', 'danger')
    
    return redirect(url_for('listar_npcs'))

@app.route('/api/npc/<int:id>/mover', methods=['POST'])
def mover_npc(id):
    """Move um NPC para outro local"""
    if not verificar_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    dados = request.json or {}
    novo_local_id = dados.get('local_id')
    
    if not novo_local_id:
        return jsonify({'success': False, 'message': 'ID do local é obrigatório'}), 400
    
    try:
        NPC.mover_para_local(id, int(novo_local_id))
        return jsonify({'success': True, 'message': 'NPC movido com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==========================================
# Rotas - Mapas (Módulo 4)
# ==========================================

@app.route('/mapas')
def listar_mapas():
    """Lista todos os mapas"""
    if not verificar_login():
        return redirect(url_for('login'))
    
    campanha = campanha_da_sessao()
    mapas = Mapa.listar_por_campanha(campanha['id']) if campanha else []
    return render_template('mapas_index.html', mapas=mapas, sem_campanha=campanha is None)

@app.route('/mapa/<int:id>')
def ver_mapa(id):
    """Visualiza um mapa"""
    if not verificar_login():
        return redirect(url_for('login'))

    mapa = Mapa.buscar_por_id(id)
    if not mapa or not pertence_a_campanha_ativa(mapa):
        flash('Mapa não encontrado nesta campanha.', 'danger')
        return redirect(url_for('listar_mapas'))
    
    return render_template('mapa_detalhe.html', mapa=mapa)

@app.route('/mapa/novo', methods=['GET', 'POST'])
def novo_mapa():
    """Cria um novo mapa"""
    if not verificar_admin():
        flash('Apenas administradores podem criar mapas.', 'danger')
        return redirect(url_for('listar_mapas'))

    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('listar_campanhas'))
    
    if request.method == 'POST':
        # Verifica se há upload de arquivo
        url_imagem = None
        
        if 'arquivo' in request.files and request.files['arquivo'].filename:
            file = request.files['arquivo']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"mapa_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                url_imagem = f"/static/uploads/{filename}"
            else:
                flash('Tipo de arquivo inválido. Use PNG, JPG, JPEG, GIF ou WEBP.', 'danger')
                locais = Local.listar_por_campanha(session.get('campanha_id'))
                return render_template('mapa_novo.html', locais=locais)
        else:
            flash('É necessário fazer upload de uma imagem.', 'danger')
            locais = Local.listar_por_campanha(session.get('campanha_id'))
            return render_template('mapa_novo.html', locais=locais)
        
        dados = {
            'nome_mapa': request.form.get('nome_mapa'),
            'tipo_mapa': request.form.get('tipo_mapa'),
            'descricao': request.form.get('descricao'),
            'local_associado_id': request.form.get('local_associado_id') or None,
            'url_imagem': url_imagem,
            'id_campanha': campanha['id']
        }
        
        if dados['local_associado_id']:
            dados['local_associado_id'] = int(dados['local_associado_id'])
        
        if not dados['nome_mapa']:
            flash('Nome do mapa é obrigatório.', 'danger')
            locais = Local.listar_por_campanha(session.get('campanha_id'))
            return render_template('mapa_novo.html', locais=locais)
        
        try:
            mapa_id = Mapa.criar(dados)
            flash('Mapa criado com sucesso!', 'success')
            return redirect(url_for('ver_mapa', id=mapa_id))
        except Exception as e:
            flash(f'Erro ao criar mapa: {str(e)}', 'danger')
    
    locais = Local.listar_por_campanha(session.get('campanha_id'))
    return render_template('mapa_novo.html', locais=locais)

@app.route('/mapa/<int:id>/editar', methods=['GET', 'POST'])
def editar_mapa(id):
    """Edita um mapa existente"""
    if not verificar_admin():
        flash('Apenas administradores podem editar mapas.', 'danger')
        return redirect(url_for('listar_mapas'))
    
    mapa = Mapa.buscar_por_id(id)
    if not mapa or not pertence_a_campanha_ativa(mapa):
        flash('Mapa não encontrado nesta campanha.', 'danger')
        return redirect(url_for('listar_mapas'))
    
    if request.method == 'POST':
        url_imagem = mapa.get('url_imagem')  # Mantém a imagem atual por padrão
        
        # Verifica se há novo upload
        if 'arquivo' in request.files and request.files['arquivo'].filename:
            file = request.files['arquivo']
            if file and allowed_file(file.filename):
                # Remove a imagem antiga se existir
                if mapa.get('url_imagem') and mapa['url_imagem'].startswith('/static/uploads/'):
                    arquivo_antigo = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                                 mapa['url_imagem'].lstrip('/'))
                    if os.path.exists(arquivo_antigo):
                        try:
                            os.remove(arquivo_antigo)
                        except:
                            pass
                
                filename = secure_filename(f"mapa_{id}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                url_imagem = f"/static/uploads/{filename}"
            else:
                flash('Tipo de arquivo inválido. Use PNG, JPG, JPEG, GIF ou WEBP.', 'danger')
                locais = Local.listar_por_campanha(session.get('campanha_id'))
                return render_template('mapa_editar.html', mapa=mapa, locais=locais)
        
        dados = {
            'nome_mapa': request.form.get('nome_mapa'),
            'tipo_mapa': request.form.get('tipo_mapa'),
            'descricao': request.form.get('descricao'),
            'local_associado_id': request.form.get('local_associado_id') or None,
            'url_imagem': url_imagem
        }
        
        if dados['local_associado_id']:
            dados['local_associado_id'] = int(dados['local_associado_id'])
        
        if not dados['nome_mapa']:
            flash('Nome do mapa é obrigatório.', 'danger')
            locais = Local.listar_por_campanha(session.get('campanha_id'))
            return render_template('mapa_editar.html', mapa=mapa, locais=locais)
        
        try:
            Mapa.atualizar(id, dados)
            flash('Mapa atualizado com sucesso!', 'success')
            return redirect(url_for('ver_mapa', id=id))
        except Exception as e:
            flash(f'Erro ao atualizar mapa: {str(e)}', 'danger')
    
    locais = Local.listar_por_campanha(session.get('campanha_id'))
    return render_template('mapa_editar.html', mapa=mapa, locais=locais)

@app.route('/mapa/<int:id>/deletar', methods=['POST'])
def deletar_mapa(id):
    """Deleta um mapa"""
    if not verificar_admin():
        flash('Apenas administradores podem deletar mapas.', 'danger')
        return redirect(url_for('listar_mapas'))
    
    mapa = Mapa.buscar_por_id(id)
    if not mapa or not pertence_a_campanha_ativa(mapa):
        flash('Mapa não encontrado nesta campanha.', 'danger')
        return redirect(url_for('listar_mapas'))
    
    try:
        # Tenta deletar o arquivo físico se existir
        if mapa.get('url_imagem') and mapa['url_imagem'].startswith('/static/uploads/'):
            arquivo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                      mapa['url_imagem'].lstrip('/'))
            if os.path.exists(arquivo_path):
                try:
                    os.remove(arquivo_path)
                except:
                    pass  # Ignora erros ao deletar arquivo
        
        Mapa.deletar(id)
        flash('Mapa deletado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao deletar mapa: {str(e)}', 'danger')
    
    return redirect(url_for('listar_mapas'))

# ==========================================
# APIs - Busca Global
# ==========================================

@app.route('/api/busca')
def busca_global():
    """Busca global em todos os módulos"""
    if not verificar_login():
        return jsonify({'results': [], 'erro': 'login necessário'}), 401

    termo = request.args.get('q', '')
    
    if not termo:
        return jsonify({'results': []})

    campanha = campanha_da_sessao()
    if not campanha:
        return jsonify({'results': []})
    campanha_id = campanha['id']
    
    resultados = []
    
    # Busca em locais
    locais = Local.buscar(termo, campanha_id)
    for local in locais:
        resultados.append({
            'tipo': 'local',
            'id': local['id'],
            'nome': local['nome'],
            'descricao': local.get('descricao_publica', '')[:100]
        })
    
    # Busca em NPCs
    npcs = NPC.buscar(termo, campanha_id)
    for npc in npcs:
        resultados.append({
            'tipo': 'npc',
            'id': npc['id'],
            'nome': npc['nome'],
            'descricao': npc.get('descricao_breve', '')[:100]
        })
    
    # Busca em mapas
    mapas = Mapa.buscar(termo, campanha_id)
    for mapa in mapas:
        resultados.append({
            'tipo': 'mapa',
            'id': mapa['id'],
            'nome': mapa['nome_mapa'],
            'descricao': mapa.get('descricao', '')[:100]
        })
    
    # Busca em personagens
    query_personagens = "SELECT * FROM personagens WHERE nome LIKE %s AND id_campanha = %s"
    termo_like = f"%{termo}%"
    personagens = Database.execute_query(query_personagens, (termo_like, campanha_id))
    for personagem in personagens:
        resultados.append({
            'tipo': 'personagem',
            'id': personagem['id'],
            'nome': personagem['nome'],
            'descricao': personagem.get('biografia', '')[:100] if personagem.get('biografia') else ''
        })
    
    return jsonify({'results': resultados})

# ==========================================
# Rotas - Autenticação
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        usuario = Usuario.buscar_por_username(username)
        
        if usuario and Usuario.verificar_senha(usuario['hashed_password'], password):
            session['user_id'] = usuario['id']
            session['username'] = usuario['username']
            session['role'] = usuario['role']
            
            Usuario.atualizar_last_login(usuario['id'])
            
            flash(f'Bem-vindo, {usuario["username"]}!', 'success')
            return redirect(url_for('listar_campanhas'))
        else:
            flash('Usuário ou senha incorretos.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de novos usuários"""
    if request.method == 'POST':
        dados = {
            'username': request.form.get('username'),
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'nome_completo': request.form.get('nome_completo'),
            'role': 'usuario'  # Novos usuários são sempre 'usuario'
        }
        
        try:
            Usuario.criar(dados)
            flash('Usuário criado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Erro ao criar usuário: {str(e)}', 'danger')
    
    return render_template('register.html')

# ==========================================
# Helpers - Verificação de Permissão
# ==========================================

@app.context_processor
def injetar_campanha_ativa():
    if not session.get('user_id'):
        return {'campanha_ativa': None, 'tema_ativo': 'padrao'}
    campanha = campanha_da_sessao()
    tema = (campanha or {}).get('tema') or 'padrao'
    if tema not in Campanha.TEMAS:
        tema = 'padrao'
    return {'campanha_ativa': campanha, 'tema_ativo': tema}

def _ficha_oculta(personagem: dict) -> bool:
    """Ficha de criatura do bestiário que o mestre ainda não revelou aos jogadores."""
    if not personagem or verificar_admin() or not personagem.get('id_campanha'):
        return False
    return personagem['id'] in Bestiario.fichas_bloqueadas(personagem['id_campanha'])

def _usuario_pode_gerenciar_personagem(personagem: dict) -> bool:
    if not personagem:
        return False
    if verificar_admin():
        return True
    try:
        personagem_owner_id = personagem.get('id_usuario_jogador')
        if personagem_owner_id is None:
            return False
        return int(personagem_owner_id) == int(session.get('user_id', 0))
    except (TypeError, ValueError):
        return False

# ==========================================
# Rotas - Upload de Imagens
# ==========================================

@app.route('/api/upload', methods=['POST'])
def upload_imagem():
    """Endpoint para upload de imagens"""
    if not verificar_login():
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    if not request.files.get('file'):
        return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    entidade_tipo = request.form.get('entidade_tipo')
    entidade_id = request.form.get('entidade_id')
    
    if not entidade_tipo or not entidade_id:
        return jsonify({'success': False, 'message': 'entidade_tipo e entidade_id são obrigatórios'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{entidade_tipo}_{entidade_id}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        path_url = f"/static/uploads/{filename}"
        
        dados = {
            'path_url': path_url,
            'alt_text': request.form.get('alt_text', ''),
            'titulo': request.form.get('titulo', ''),
            'descricao': request.form.get('descricao', ''),
            'entidade_tipo': entidade_tipo,
            'entidade_id': entidade_id,
            'file_size': os.path.getsize(filepath),
            'mime_type': file.content_type,
        }
        
        Imagem.criar(dados)
        
        return jsonify({'success': True, 'message': 'Imagem enviada com sucesso!', 'path': path_url})
    
    return jsonify({'success': False, 'message': 'Arquivo inválido'}), 400

@app.route('/api/imagens/<entidade_tipo>/<int:entidade_id>')
def listar_imagens_entidade(entidade_tipo, entidade_id):
    """Lista imagens de uma entidade"""
    imagens = Imagem.buscar_por_entidade(entidade_tipo, entidade_id)
    return jsonify(imagens)

# ==========================================
# Rotas - Campanhas
# ==========================================

@app.route('/campanhas', methods=['GET', 'POST'])
def listar_campanhas():
    """Lista as campanhas e permite entrar em uma delas"""
    if not verificar_login():
        return redirect(url_for('login'))

    if request.method == 'POST':
        if not verificar_admin():
            flash('Apenas administradores podem criar campanhas.', 'danger')
            return redirect(url_for('listar_campanhas'))
        nome = (request.form.get('nome_campanha') or '').strip()
        if not nome:
            flash('Nome da campanha é obrigatório.', 'danger')
            return redirect(url_for('listar_campanhas'))
        try:
            pontos = int(request.form.get('pontos_iniciais') or 150)
        except (TypeError, ValueError):
            pontos = 150
        novo_id = Campanha.criar({
            'nome_campanha': nome,
            'id_mestre': session.get('user_id'),
            'pontos_iniciais': pontos,
            'descricao': request.form.get('descricao'),
            'status': 'Ativa',
        })
        session['campanha_id'] = novo_id
        flash(f'Campanha {nome} criada. Você já está nela.', 'success')
        return redirect(url_for('index'))
    
    campanhas = Campanha.listar_todas()
    return render_template('campanhas_index.html', campanhas=campanhas)

@app.route('/campanha/<int:id>/entrar', methods=['POST'])
def entrar_campanha(id):
    """Define a campanha ativa da sessão"""
    if not verificar_login():
        return redirect(url_for('login'))

    campanha = Campanha.buscar_por_id(id)
    if not campanha:
        flash('Campanha não encontrada.', 'danger')
        return redirect(url_for('listar_campanhas'))

    session['campanha_id'] = campanha['id']
    flash(f'Você entrou na campanha {campanha["nome_campanha"]}.', 'success')
    return redirect(url_for('index'))

@app.route('/campanha/<int:id>', methods=['GET', 'POST'])
def ver_campanha(id):
    """Visualiza e atualiza uma campanha"""
    if not verificar_login():
        return redirect(url_for('login'))
    
    campanha = Campanha.buscar_por_id(id)
    if not campanha:
        flash('Campanha não encontrada.', 'danger')
        return redirect(url_for('listar_campanhas'))

    if request.method == 'POST':
        if not verificar_admin():
            flash('Apenas administradores podem alterar a campanha.', 'danger')
            return redirect(url_for('ver_campanha', id=id))

        if request.form.get('usuario_id'):
            try:
                usuario_id = int(request.form.get('usuario_id'))
            except (TypeError, ValueError):
                flash('ID do jogador inválido.', 'danger')
                return redirect(url_for('ver_campanha', id=id))
            Campanha.convidar_jogador(id, usuario_id)
            flash('Jogador convidado para a campanha.', 'success')
            return redirect(url_for('ver_campanha', id=id))

        nome = (request.form.get('nome_campanha') or '').strip()
        if not nome:
            flash('Nome da campanha é obrigatório.', 'danger')
            return redirect(url_for('ver_campanha', id=id))
        try:
            pontos = int(request.form.get('pontos_iniciais'))
        except (TypeError, ValueError):
            flash('Pontos iniciais inválidos.', 'danger')
            return redirect(url_for('ver_campanha', id=id))
        if pontos < 0:
            flash('Pontos iniciais não podem ser negativos.', 'danger')
            return redirect(url_for('ver_campanha', id=id))

        tema = request.form.get('tema') or campanha.get('tema') or 'padrao'
        if tema not in Campanha.TEMAS:
            tema = 'padrao'

        Campanha.atualizar(id, {
            'nome_campanha': nome,
            'pontos_iniciais': pontos,
            'descricao': request.form.get('descricao'),
            'status': campanha.get('status') or 'Ativa',
            'tema': tema,
        })
        flash('Campanha atualizada.', 'success')
        return redirect(url_for('ver_campanha', id=id))
    
    # Busca personagens da campanha
    query = """
        SELECT p.*, u.username 
        FROM personagens p 
        LEFT JOIN usuarios u ON p.id_usuario_jogador = u.id
        WHERE p.id_campanha = %s
        ORDER BY p.status_criacao, p.nome
    """
    personagens = Database.execute_query(query, (id,))
    
    return render_template('campanha_detalhe.html', campanha=campanha, personagens=personagens,
                           temas=Campanha.TEMAS)

@app.route('/meus-personagens')
def meus_personagens():
    """Lista personagens pendentes/em andamento do jogador"""
    if not verificar_login():
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    
    query = """
        SELECT p.*, c.nome_campanha, c.pontos_iniciais
        FROM personagens p
        JOIN campanhas c ON p.id_campanha = c.id
        WHERE p.id_usuario_jogador = %s
        AND p.status_criacao IN ('Pendente', 'Em_Andamento')
        ORDER BY p.created_at DESC
    """
    personagens = Database.execute_query(query, (user_id,))
    
    return render_template('meus_personagens.html', personagens=personagens)

@app.route('/api/calcular-pontos', methods=['POST'])
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

@app.route('/api/pericias/catalogo')
def listar_pericias_catalogo():
    itens = PericiaCatalogo.listar_todas()
    return jsonify(itens)

# ==========================================
# APIs - Catálogo de Vantagens e Desvantagens
# ==========================================

@app.route('/api/vantagens-desvantagens/catalogo')
def listar_vantagens_desvantagens_catalogo():
    """Retorna lista de vantagens e desvantagens do catálogo"""
    tipo = request.args.get('tipo', None)
    
    if tipo == 'Vantagem':
        itens = VantagemDesvantagemCatalogo.listar_vantagens()
    elif tipo == 'Desvantagem':
        itens = VantagemDesvantagemCatalogo.listar_desvantagens()
    else:
        itens = VantagemDesvantagemCatalogo.listar_todas()
    
    return jsonify(itens)

@app.route('/api/personagem/<int:personagem_id>/pericias/by-catalog', methods=['POST'])
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
        
        cat = PericiaCatalogo.buscar_por_id(cat_id)
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

@app.route('/api/itens/catalogo')
def listar_itens_catalogo():
    itens = ItemCatalogo.listar_todos()
    return jsonify(itens)


@app.route('/api/personagem/<int:personagem_id>/inventario/by-catalog', methods=['POST'])
def adicionar_item_por_catalogo(personagem_id):
    if not verificar_login():
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401

    dados = request.json or {}
    try:
        catalogo_id = int(dados['catalogo_id'])
        quantidade = max(1, int(dados.get('quantidade', 1)))

        item_catalogo = ItemCatalogo.buscar_por_id(catalogo_id)
        if not item_catalogo:
            return jsonify({'success': False, 'message': 'Item não encontrado no catálogo'}), 404

        preco_unitario = Decimal(str(item_catalogo.get('preco') or 0))
        peso_unitario = Decimal(str(item_catalogo.get('peso') or 0))

        personagem = Personagem.buscar_por_id(personagem_id)
        if not personagem:
            return jsonify({'success': False, 'message': 'Personagem não encontrado'}), 404

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

@app.route('/api/personagem/<int:personagem_id>/inventario', methods=['GET'])
def listar_inventario(personagem_id):
    atributos = Atributos.buscar_por_personagem(personagem_id)
    dados = _processar_inventario_personagem(personagem_id, atributos)
    personagem = Personagem.buscar_por_id(personagem_id)
    pode_equipar = _usuario_pode_gerenciar_personagem(personagem)
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

@app.route('/api/personagem/<int:personagem_id>/inventario', methods=['POST'])
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

@app.route('/api/inventario/<int:item_id>', methods=['DELETE'])
def remover_item_inventario(item_id):
    if not verificar_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    try:
        Inventario.deletar(item_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/inventario/<int:item_id>/usar', methods=['POST'])
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

@app.route('/api/inventario/<int:item_id>/consumir', methods=['POST'])
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

@app.route('/api/inventario/<int:item_id>/equipar', methods=['POST'])
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
    if not _usuario_pode_gerenciar_personagem(personagem):
        return jsonify({'success': False, 'message': 'Sem permissão para equipar este item'}), 403

    try:
        Equipamento.equipar(personagem['id'], item_id, slot)
        return jsonify({'success': True, 'slot': slot})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/inventario/<int:item_id>/desequipar', methods=['POST'])
def desequipar_item_inventario(item_id):
    if not verificar_login():
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401

    item = Inventario.buscar_por_id(item_id)
    if not item:
        return jsonify({'success': False, 'message': 'Item não encontrado'}), 404

    personagem = Personagem.buscar_por_id(item['personagem_id'])
    if not _usuario_pode_gerenciar_personagem(personagem):
        return jsonify({'success': False, 'message': 'Sem permissão para alterar este item'}), 403

    try:
        Equipamento.desequipar(item_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==========================================
# Helpers - Cálculo de Carga (GURPS)
# ==========================================

def _calcular_nivel_carga(peso_total: float, ST: int) -> str:
    """Retorna o nível de carga de acordo com o Peso Morto (PM = ST * 15)."""
    PM = ST * 15.0
    if peso_total <= 0:
        return 'Nenhuma'
    if peso_total <= PM * 0.1:
        return 'Leve (10%)'
    if peso_total <= PM * 0.2:
        return 'Média (20%)'
    if peso_total <= PM * 0.3:
        return 'Pesada (30%)'
    if peso_total <= PM * 0.4:
        return 'Extrema (40%)'
    return 'Sobrecarga (>40%)'


def _obter_valor_atributo_para_pericia(atributos, atributo_codigo):
    """Retorna o valor atual do atributo base utilizado pela perícia."""
    if not atributos or not atributo_codigo:
        return None
    
    codigo = (atributo_codigo or '').upper()
    alias = {
        'PER': 'Per',
        'PERCEPCAO': 'Per',
        'WILL': 'Will',
        'VONTADE': 'Will',
        'VT': 'Will'
    }
    
    if codigo in atributos:
        return atributos.get(codigo)
    
    if codigo in alias:
        return atributos.get(alias[codigo]) or atributos.get(alias[codigo].upper())
    
    # fallback para atributos básicos
    return atributos.get(codigo) or atributos.get(codigo.title())


def _processar_inventario_personagem(personagem_id, atributos=None):
    """Enriquece o inventário com efeitos e calcula resumos."""
    itens_brutos = Inventario.listar_por_personagem(personagem_id)
    st_base = atributos['ST'] if atributos and atributos.get('ST') else 10
    bal_base = Atributos._calcular_golpe_balanco(st_base)
    gpd_base = Atributos._calcular_golpe_ponta(st_base)
    itens_enriquecidos, efeitos = enriquecer_inventario(
        itens_brutos,
        bal_base=bal_base,
        gpd_base=gpd_base
    )

    peso_total = sum(
        float(item.get('peso') or 0) * int(item.get('quantidade') or 0)
        for item in itens_brutos
    )
    valor_total = sum(
        float(item.get('preco_unitario') or 0) * int(item.get('quantidade') or 0)
        for item in itens_brutos
    )

    nivel_carga = _calcular_nivel_carga(peso_total, st_base)

    return {
        'itens': itens_enriquecidos,
        'peso_total': peso_total,
        'valor_total': valor_total,
        'nivel_carga': nivel_carga,
        'efeitos': efeitos
    }

# ==========================================
# Admin - Sessões e Pontos de Personagem
# ==========================================

@app.route('/admin/sessoes')
def admin_sessoes_form():
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('index'))
    pcs = Database.execute_query("SELECT id, nome FROM personagens WHERE is_pc = TRUE ORDER BY nome")
    return render_template('admin_sessoes_distribuir.html', pcs=pcs)

@app.route('/admin/sessoes/historico')
def admin_sessoes_historico():
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('index'))
    linhas = SessaoLog.listar_historico_sessoes()
    # Agrupa por sessão para renderização simples
    sessoes = {}
    for l in linhas:
        sid = l['id']
        if sid not in sessoes:
            sessoes[sid] = {
                'id': sid,
                'data_sessao': l['data_sessao'],
                'descricao': l['descricao'],
                'itens': []
            }
        if l.get('personagem_id'):
            sessoes[sid]['itens'].append({
                'personagem_nome': l.get('personagem_nome'),
                'pontos_ganhos': l.get('pontos_ganhos')
            })
    return render_template('admin_sessoes_historico.html', sessoes=list(sessoes.values()))

@app.route('/api/admin/sessoes/distribuir', methods=['POST'])
def api_distribuir_pontos_sessao():
    if not verificar_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    dados = request.json or {}
    try:
        data_sessao = dados['data_sessao']
        descricao = dados.get('descricao', '')
        distribuicoes = dados.get('distribuicoes', [])
        # valida formato
        dist_validas = [
            { 'personagem_id': int(d['personagem_id']), 'pontos': int(d.get('pontos', 0)) }
            for d in distribuicoes if int(d.get('pontos', 0)) != 0
        ]
        if len(dist_validas) == 0:
            return jsonify({'success': False, 'message': 'Nenhum ponto a distribuir'}), 400
        sessao_id = SessaoLog.criar_transacional(data_sessao, descricao, dist_validas)
        return jsonify({'success': True, 'sessao_id': sessao_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==========================================
# Admin - Dashboard
# ==========================================

@app.route('/admin')
def admin_dashboard():
    """Dashboard administrativo"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('index'))
    
    # Estatísticas
    total_personagens = len(Personagem.listar_todos())
    personagens_pendentes = len(Personagem.listar_por_status_criacao('Pendente'))
    total_usuarios = len(Usuario.listar_todos())
    total_campanhas = len(Campanha.listar_todas())
    total_itens = len(ItemCatalogo.listar_todos())
    total_pericias = len(PericiaCatalogo.listar_todas())
    total_vantagens = len(VantagemDesvantagemCatalogo.listar_todas())
    
    return render_template('admin_dashboard.html',
                         total_personagens=total_personagens,
                         personagens_pendentes=personagens_pendentes,
                         total_usuarios=total_usuarios,
                         total_campanhas=total_campanhas,
                         total_itens=total_itens,
                         total_pericias=total_pericias,
                         total_vantagens=total_vantagens)

# ==========================================
# Admin - Gerenciamento de Catálogo de Itens
# ==========================================

@app.route('/admin/itens')
def admin_itens_lista():
    """Lista todos os itens do catálogo"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('index'))
    
    itens = ItemCatalogo.listar_todos()
    return render_template('admin_itens_lista.html', itens=itens)

@app.route('/admin/itens/novo', methods=['GET', 'POST'])
def admin_itens_novo():
    """Cria um novo item no catálogo"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('admin_itens_lista'))
    
    if request.method == 'POST':
        try:
            item_id = ItemCatalogo.criar(
                nome=request.form.get('nome'),
                categoria=request.form.get('categoria', ''),
                preco=float(request.form.get('preco', 0)),
                peso=float(request.form.get('peso', 0)),
                descricao=request.form.get('descricao', ''),
                tipo_item=request.form.get('tipo_item', 'outro'),
                dano_bal_mod=int(request.form.get('dano_bal_mod', 0)) if request.form.get('dano_bal_mod') else None,
                dano_bal_tipo=request.form.get('dano_bal_tipo', '') or None,
                dano_gdp_mod=int(request.form.get('dano_gdp_mod', 0)) if request.form.get('dano_gdp_mod') else None,
                dano_gdp_tipo=request.form.get('dano_gdp_tipo', '') or None,
                rd_mod=int(request.form.get('rd_mod', 0)) if request.form.get('rd_mod') else None,
                rd_tipo=request.form.get('rd_tipo', '') or None
            )
            flash('Item criado com sucesso!', 'success')
            return redirect(url_for('admin_itens_editar', id=item_id))
        except Exception as e:
            flash(f'Erro ao criar item: {str(e)}', 'danger')
    
    return render_template('admin_itens_form.html', item=None)

@app.route('/admin/itens/<int:id>/editar', methods=['GET', 'POST'])
def admin_itens_editar(id):
    """Edita um item do catálogo"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('admin_itens_lista'))
    
    item = ItemCatalogo.buscar_por_id(id)
    if not item:
        flash('Item não encontrado.', 'danger')
        return redirect(url_for('admin_itens_lista'))
    
    if request.method == 'POST':
        try:
            ItemCatalogo.atualizar(
                item_id=id,
                nome=request.form.get('nome'),
                categoria=request.form.get('categoria'),
                preco=float(request.form.get('preco', 0)) if request.form.get('preco') else None,
                peso=float(request.form.get('peso', 0)) if request.form.get('peso') else None,
                descricao=request.form.get('descricao'),
                tipo_item=request.form.get('tipo_item'),
                dano_bal_mod=int(request.form.get('dano_bal_mod', 0)) if request.form.get('dano_bal_mod') else None,
                dano_bal_tipo=request.form.get('dano_bal_tipo', '') or None,
                dano_gdp_mod=int(request.form.get('dano_gdp_mod', 0)) if request.form.get('dano_gdp_mod') else None,
                dano_gdp_tipo=request.form.get('dano_gdp_tipo', '') or None,
                rd_mod=int(request.form.get('rd_mod', 0)) if request.form.get('rd_mod') else None,
                rd_tipo=request.form.get('rd_tipo', '') or None
            )
            flash('Item atualizado com sucesso!', 'success')
            return redirect(url_for('admin_itens_editar', id=id))
        except Exception as e:
            flash(f'Erro ao atualizar item: {str(e)}', 'danger')
    
    return render_template('admin_itens_form.html', item=item)

@app.route('/admin/itens/<int:id>/deletar', methods=['POST'])
def admin_itens_deletar(id):
    """Deleta um item do catálogo"""
    if not verificar_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        ItemCatalogo.deletar(id)
        flash('Item deletado com sucesso!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# ==========================================
# Admin - Gerenciamento de Catálogo de Perícias
# ==========================================

@app.route('/admin/pericias')
def admin_pericias_lista():
    """Lista todas as perícias do catálogo"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('index'))
    
    pericias = PericiaCatalogo.listar_todas()
    return render_template('admin_pericias_lista.html', pericias=pericias)

@app.route('/admin/pericias/novo', methods=['GET', 'POST'])
def admin_pericias_novo():
    """Cria uma nova perícia no catálogo"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('admin_pericias_lista'))
    
    if request.method == 'POST':
        try:
            pericia_id = PericiaCatalogo.criar(
                nome=request.form.get('nome'),
                atributo_base=request.form.get('atributo_base'),
                dificuldade=request.form.get('dificuldade'),
                custo_texto=request.form.get('custo_texto', ''),
                descricao=request.form.get('descricao', '')
            )
            flash('Perícia criada com sucesso!', 'success')
            return redirect(url_for('admin_pericias_editar', id=pericia_id))
        except Exception as e:
            flash(f'Erro ao criar perícia: {str(e)}', 'danger')
    
    return render_template('admin_pericias_form.html', pericia=None)

@app.route('/admin/pericias/<int:id>/editar', methods=['GET', 'POST'])
def admin_pericias_editar(id):
    """Edita uma perícia do catálogo"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('admin_pericias_lista'))
    
    pericia = PericiaCatalogo.buscar_por_id(id)
    if not pericia:
        flash('Perícia não encontrada.', 'danger')
        return redirect(url_for('admin_pericias_lista'))
    
    if request.method == 'POST':
        try:
            PericiaCatalogo.atualizar(
                pericia_id=id,
                nome=request.form.get('nome'),
                atributo_base=request.form.get('atributo_base'),
                dificuldade=request.form.get('dificuldade'),
                custo_texto=request.form.get('custo_texto'),
                descricao=request.form.get('descricao')
            )
            flash('Perícia atualizada com sucesso!', 'success')
            return redirect(url_for('admin_pericias_editar', id=id))
        except Exception as e:
            flash(f'Erro ao atualizar perícia: {str(e)}', 'danger')
    
    return render_template('admin_pericias_form.html', pericia=pericia)

@app.route('/admin/pericias/<int:id>/deletar', methods=['POST'])
def admin_pericias_deletar(id):
    """Deleta uma perícia do catálogo"""
    if not verificar_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        PericiaCatalogo.deletar(id)
        flash('Perícia deletada com sucesso!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# ==========================================
# Admin - Gerenciamento de Catálogo de Vantagens/Desvantagens
# ==========================================

@app.route('/admin/vantagens')
def admin_vantagens_lista():
    """Lista todas as vantagens/desvantagens do catálogo"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('index'))
    
    vantagens = VantagemDesvantagemCatalogo.listar_todas()
    return render_template('admin_vantagens_lista.html', vantagens=vantagens)

@app.route('/admin/vantagens/novo', methods=['GET', 'POST'])
def admin_vantagens_novo():
    """Cria uma nova vantagem/desvantagem no catálogo"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('admin_vantagens_lista'))
    
    if request.method == 'POST':
        try:
            vd_id = VantagemDesvantagemCatalogo.criar(
                nome=request.form.get('nome'),
                tipo=request.form.get('tipo'),
                custo_base=int(request.form.get('custo_base', 0)),
                custo_texto=request.form.get('custo_texto', ''),
                descricao=request.form.get('descricao', ''),
                categoria=request.form.get('categoria', '')
            )
            flash('Vantagem/Desvantagem criada com sucesso!', 'success')
            return redirect(url_for('admin_vantagens_editar', id=vd_id))
        except Exception as e:
            flash(f'Erro ao criar vantagem/desvantagem: {str(e)}', 'danger')
    
    return render_template('admin_vantagens_form.html', vantagem=None)

@app.route('/admin/vantagens/<int:id>/editar', methods=['GET', 'POST'])
def admin_vantagens_editar(id):
    """Edita uma vantagem/desvantagem do catálogo"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('admin_vantagens_lista'))
    
    vantagem = VantagemDesvantagemCatalogo.buscar_por_id(id)
    if not vantagem:
        flash('Vantagem/Desvantagem não encontrada.', 'danger')
        return redirect(url_for('admin_vantagens_lista'))
    
    if request.method == 'POST':
        try:
            VantagemDesvantagemCatalogo.atualizar(
                vd_id=id,
                nome=request.form.get('nome'),
                tipo=request.form.get('tipo'),
                custo_base=int(request.form.get('custo_base', 0)) if request.form.get('custo_base') else None,
                custo_texto=request.form.get('custo_texto'),
                descricao=request.form.get('descricao'),
                categoria=request.form.get('categoria')
            )
            flash('Vantagem/Desvantagem atualizada com sucesso!', 'success')
            return redirect(url_for('admin_vantagens_editar', id=id))
        except Exception as e:
            flash(f'Erro ao atualizar vantagem/desvantagem: {str(e)}', 'danger')
    
    return render_template('admin_vantagens_form.html', vantagem=vantagem)

@app.route('/admin/vantagens/<int:id>/deletar', methods=['POST'])
def admin_vantagens_deletar(id):
    """Deleta uma vantagem/desvantagem do catálogo"""
    if not verificar_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        VantagemDesvantagemCatalogo.deletar(id)
        flash('Vantagem/Desvantagem deletada com sucesso!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# ==========================================
# Admin - Gerenciamento de Usuários
# ==========================================

@app.route('/admin/usuarios')
def admin_usuarios_lista():
    """Lista todos os usuários"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('index'))
    
    usuarios = Usuario.listar_todos()
    return render_template('admin_usuarios_lista.html', usuarios=usuarios)

@app.route('/admin/usuarios/<int:id>/pontos', methods=['GET', 'POST'])
def admin_usuarios_pontos(id):
    """Gerencia pontos de um usuário"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('index'))
    
    usuario = Usuario.buscar_por_id(id)
    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('admin_usuarios_lista'))
    
    if request.method == 'POST':
        try:
            acao = request.form.get('acao')
            quantidade = int(request.form.get('quantidade', 0))
            observacao = request.form.get('observacao', '')
            
            if acao == 'adicionar':
                Usuario.adicionar_pontos(id, quantidade)
                flash(f'Adicionados {quantidade} pontos ao usuário {usuario["username"]}.', 'success')
            elif acao == 'remover':
                Usuario.remover_pontos(id, quantidade)
                flash(f'Removidos {quantidade} pontos do usuário {usuario["username"]}.', 'success')
            elif acao == 'definir':
                Usuario.definir_pontos(id, quantidade)
                flash(f'Pontos do usuário {usuario["username"]} definidos para {quantidade}.', 'success')
            else:
                flash('Ação inválida.', 'danger')
            
            # Atualiza dados do usuário
            usuario = Usuario.buscar_por_id(id)
            return redirect(url_for('admin_usuarios_pontos', id=id))
        except Exception as e:
            flash(f'Erro ao gerenciar pontos: {str(e)}', 'danger')
    
    # Busca histórico de alterações (opcional - pode ser implementado depois)
    pontos_atual = Usuario.get_pontos_disponiveis(id)
    
    return render_template('admin_usuarios_pontos.html', usuario=usuario, pontos_atual=pontos_atual)

@app.route('/admin/usuarios/<int:id>/editar', methods=['GET', 'POST'])
def admin_usuarios_editar(id):
    """Edita um usuário"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('admin_usuarios_lista'))
    
    usuario = Usuario.buscar_por_id(id)
    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('admin_usuarios_lista'))
    
    if request.method == 'POST':
        try:
            Usuario.atualizar(
                user_id=id,
                dados={
                    'role': request.form.get('role'),
                    'is_active': request.form.get('is_active') == '1',
                    'nome_completo': request.form.get('nome_completo'),
                    'email': request.form.get('email')
                }
            )
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('admin_usuarios_editar', id=id))
        except Exception as e:
            flash(f'Erro ao atualizar usuário: {str(e)}', 'danger')
    
    return render_template('admin_usuarios_form.html', usuario=usuario)

# ==========================================
# Admin - Gerenciamento de Campanhas
# ==========================================

@app.route('/admin/campanhas')
def admin_campanhas_lista():
    """Lista todas as campanhas"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('index'))
    
    campanhas = Campanha.listar_todas()
    usuarios = Usuario.listar_todos()
    return render_template('admin_campanhas_lista.html', campanhas=campanhas, usuarios=usuarios)

@app.route('/admin/campanhas/novo', methods=['GET', 'POST'])
def admin_campanhas_novo():
    """Cria uma nova campanha"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('admin_campanhas_lista'))
    
    usuarios = Usuario.listar_todos()
    
    if request.method == 'POST':
        try:
            Campanha.criar({
                'nome_campanha': request.form.get('nome_campanha'),
                'id_mestre': int(request.form.get('id_mestre')),
                'pontos_iniciais': int(request.form.get('pontos_iniciais', 100)),
                'descricao': request.form.get('descricao', ''),
                'status': request.form.get('status', 'Ativa')
            })
            flash('Campanha criada com sucesso!', 'success')
            return redirect(url_for('admin_campanhas_lista'))
        except Exception as e:
            flash(f'Erro ao criar campanha: {str(e)}', 'danger')
    
    return render_template('admin_campanhas_form.html', campanha=None, usuarios=usuarios)

@app.route('/admin/campanhas/<int:id>/editar', methods=['GET', 'POST'])
def admin_campanhas_editar(id):
    """Edita uma campanha"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('admin_campanhas_lista'))
    
    campanha = Campanha.buscar_por_id(id)
    if not campanha:
        flash('Campanha não encontrada.', 'danger')
        return redirect(url_for('admin_campanhas_lista'))
    
    usuarios = Usuario.listar_todos()
    
    if request.method == 'POST':
        try:
            Campanha.atualizar(id, {
                'nome_campanha': request.form.get('nome_campanha'),
                'pontos_iniciais': int(request.form.get('pontos_iniciais', 100)),
                'descricao': request.form.get('descricao', ''),
                'status': request.form.get('status', 'Ativa')
            })
            flash('Campanha atualizada com sucesso!', 'success')
            return redirect(url_for('admin_campanhas_editar', id=id))
        except Exception as e:
            flash(f'Erro ao atualizar campanha: {str(e)}', 'danger')
    
    return render_template('admin_campanhas_form.html', campanha=campanha, usuarios=usuarios)

# ==========================================
# Admin - Aprovar/Rejeitar Fichas de Personagem
# ==========================================

@app.route('/admin/personagens')
def admin_personagens_lista():
    """Lista todos os personagens (admin)"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('index'))
    
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'pendente':
        personagens = Personagem.listar_por_status_criacao('Pendente')
    elif status_filter == 'aprovado':
        personagens = Personagem.listar_por_status_criacao('Aprovado')
    elif status_filter == 'rejeitado':
        personagens = Personagem.listar_por_status_criacao('Rejeitado')
    else:
        personagens = Personagem.listar_todos_admin()
    
    return render_template('admin_personagens_lista.html', personagens=personagens, status_filter=status_filter)

@app.route('/admin/personagens/<int:id>/aprovar', methods=['POST'])
def admin_personagens_aprovar(id):
    """Aprova uma ficha de personagem"""
    if not verificar_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        observacoes = request.json.get('observacoes', '') if request.is_json else request.form.get('observacoes', '')
        Personagem.atualizar_status_criacao(id, 'Aprovado', observacoes)
        flash('Ficha aprovada com sucesso!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/admin/personagens/<int:id>/rejeitar', methods=['POST'])
def admin_personagens_rejeitar(id):
    """Rejeita uma ficha de personagem"""
    if not verificar_admin():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    try:
        observacoes = request.json.get('observacoes', '') if request.is_json else request.form.get('observacoes', '')
        Personagem.atualizar_status_criacao(id, 'Rejeitado', observacoes)
        flash('Ficha rejeitada.', 'warning')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# ==========================================
# Headers Anti-Cache para Desenvolvimento
# ==========================================

@app.after_request
def after_request(response):
    """Adiciona headers anti-cache em todas as respostas em modo debug"""
    if Config.DEBUG:
        # Em modo debug, sempre força recarregamento
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# ==========================================
# Execução
# ==========================================

# ==========================================
# Admin - Gerenciamento de Raças
# ==========================================

@app.route('/admin/racas')
def admin_racas_lista():
    """Lista todas as raças"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('index'))
    
    campanha = campanha_da_sessao()
    racas = Raca.listar_por_campanha(campanha['id']) if campanha else []
    return render_template('admin_racas_lista.html', racas=racas, sem_campanha=campanha is None)

@app.route('/admin/racas/novo', methods=['GET', 'POST'])
def admin_racas_novo():
    """Cria uma nova raça"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('admin_racas_lista'))

    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('listar_campanhas'))
    
    if request.method == 'POST':
        try:
            import json
            # Processa vantagens selecionadas (JSON do campo hidden)
            vantagens_json_str = request.form.get('vantagens_automaticas', '')
            vantagens_json = None
            if vantagens_json_str:
                try:
                    # Valida que é um JSON válido
                    ids = json.loads(vantagens_json_str)
                    if isinstance(ids, list) and len(ids) > 0:
                        vantagens_json = vantagens_json_str
                except:
                    pass
            
            # Processa perícias selecionadas (JSON do campo hidden)
            pericias_json_str = request.form.get('pericias_automaticas', '')
            pericias_json = None
            if pericias_json_str:
                try:
                    # Valida que é um JSON válido
                    ids = json.loads(pericias_json_str)
                    if isinstance(ids, list) and len(ids) > 0:
                        pericias_json = pericias_json_str
                except:
                    pass
            
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
                'vantagens_automaticas': vantagens_json,
                'pericias_automaticas': pericias_json,
                'observacoes': request.form.get('observacoes', ''),
                'is_active': request.form.get('is_active') == 'on',
                'id_campanha': campanha['id']
            }
            
            Raca.criar(dados)
            flash('Raça criada com sucesso!', 'success')
            return redirect(url_for('admin_racas_lista'))
        except Exception as e:
            flash(f'Erro ao criar raça: {str(e)}', 'danger')
    
    # Carrega catálogos para os selects
    vantagens = VantagemDesvantagemCatalogo.listar_vantagens()
    pericias = PericiaCatalogo.listar_todas()
    
    return render_template('admin_racas_form.html', raca=None, vantagens=vantagens, pericias=pericias,
                         vantagens_selecionadas=[], pericias_selecionadas=[])

@app.route('/admin/racas/<int:id>/editar', methods=['GET', 'POST'])
def admin_racas_editar(id):
    """Edita uma raça"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('admin_racas_lista'))
    
    raca = Raca.buscar_por_id(id)
    if not raca or not pertence_a_campanha_ativa(raca):
        flash('Raça não encontrada nesta campanha.', 'danger')
        return redirect(url_for('admin_racas_lista'))
    
    if request.method == 'POST':
        try:
            import json
            # Processa vantagens selecionadas (JSON do campo hidden)
            vantagens_json_str = request.form.get('vantagens_automaticas', '')
            vantagens_json = None
            if vantagens_json_str:
                try:
                    # Valida que é um JSON válido
                    ids = json.loads(vantagens_json_str)
                    if isinstance(ids, list) and len(ids) > 0:
                        vantagens_json = vantagens_json_str
                except:
                    pass
            
            # Processa perícias selecionadas (JSON do campo hidden)
            pericias_json_str = request.form.get('pericias_automaticas', '')
            pericias_json = None
            if pericias_json_str:
                try:
                    # Valida que é um JSON válido
                    ids = json.loads(pericias_json_str)
                    if isinstance(ids, list) and len(ids) > 0:
                        pericias_json = pericias_json_str
                except:
                    pass
            
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
                'vantagens_automaticas': vantagens_json,
                'pericias_automaticas': pericias_json,
                'observacoes': request.form.get('observacoes', ''),
                'is_active': request.form.get('is_active') == 'on'
            }
            
            Raca.atualizar(id, dados)
            flash('Raça atualizada com sucesso!', 'success')
            return redirect(url_for('admin_racas_lista'))
        except Exception as e:
            flash(f'Erro ao atualizar raça: {str(e)}', 'danger')
    
    # Carrega catálogos e parseia JSON das vantagens/perícias selecionadas
    import json
    vantagens = VantagemDesvantagemCatalogo.listar_vantagens()
    pericias = PericiaCatalogo.listar_todas()
    
    # Parseia IDs selecionados
    vantagens_selecionadas = []
    if raca.get('vantagens_automaticas'):
        try:
            vantagens_selecionadas = json.loads(raca['vantagens_automaticas'])
        except:
            vantagens_selecionadas = []
    
    pericias_selecionadas = []
    if raca.get('pericias_automaticas'):
        try:
            pericias_selecionadas = json.loads(raca['pericias_automaticas'])
        except:
            pericias_selecionadas = []
    
    return render_template('admin_racas_form.html', raca=raca, vantagens=vantagens, pericias=pericias,
                         vantagens_selecionadas=vantagens_selecionadas, pericias_selecionadas=pericias_selecionadas)

@app.route('/admin/racas/<int:id>/deletar', methods=['POST'])
def admin_racas_deletar(id):
    """Deleta uma raça (soft delete)"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('admin_racas_lista'))

    if not pertence_a_campanha_ativa(Raca.buscar_por_id(id)):
        flash('Raça não encontrada nesta campanha.', 'danger')
        return redirect(url_for('admin_racas_lista'))
    
    try:
        Raca.deletar(id)
        flash('Raça deletada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao deletar raça: {str(e)}', 'danger')
    
    return redirect(url_for('admin_racas_lista'))

# ==========================================
# Admin - Gerenciamento de Classes
# ==========================================

@app.route('/admin/classes')
def admin_classes_lista():
    """Lista todas as classes"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('index'))
    
    campanha = campanha_da_sessao()
    classes = Classe.listar_por_campanha(campanha['id']) if campanha else []
    return render_template('admin_classes_lista.html', classes=classes, sem_campanha=campanha is None)

@app.route('/admin/classes/novo', methods=['GET', 'POST'])
def admin_classes_novo():
    """Cria uma nova classe"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('admin_classes_lista'))

    campanha = exigir_campanha()
    if not campanha:
        return redirect(url_for('listar_campanhas'))
    
    if request.method == 'POST':
        try:
            import json
            # Processa vantagens selecionadas (JSON do campo hidden)
            vantagens_json_str = request.form.get('vantagens_automaticas', '')
            vantagens_json = None
            if vantagens_json_str:
                try:
                    # Valida que é um JSON válido
                    ids = json.loads(vantagens_json_str)
                    if isinstance(ids, list) and len(ids) > 0:
                        vantagens_json = vantagens_json_str
                except:
                    pass
            
            # Processa perícias selecionadas (JSON do campo hidden)
            pericias_json_str = request.form.get('pericias_automaticas', '')
            pericias_json = None
            if pericias_json_str:
                try:
                    # Valida que é um JSON válido
                    ids = json.loads(pericias_json_str)
                    if isinstance(ids, list) and len(ids) > 0:
                        pericias_json = pericias_json_str
                except:
                    pass
            
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
                'vantagens_automaticas': vantagens_json,
                'pericias_automaticas': pericias_json,
                'observacoes': request.form.get('observacoes', ''),
                'is_active': request.form.get('is_active') == 'on',
                'id_campanha': campanha['id']
            }
            
            Classe.criar(dados)
            flash('Classe criada com sucesso!', 'success')
            return redirect(url_for('admin_classes_lista'))
        except Exception as e:
            flash(f'Erro ao criar classe: {str(e)}', 'danger')
    
    # Carrega catálogos para os selects
    vantagens = VantagemDesvantagemCatalogo.listar_vantagens()
    pericias = PericiaCatalogo.listar_todas()
    
    return render_template('admin_classes_form.html', classe=None, vantagens=vantagens, pericias=pericias,
                         vantagens_selecionadas=[], pericias_selecionadas=[])

@app.route('/admin/classes/<int:id>/editar', methods=['GET', 'POST'])
def admin_classes_editar(id):
    """Edita uma classe"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('admin_classes_lista'))
    
    classe = Classe.buscar_por_id(id)
    if not classe or not pertence_a_campanha_ativa(classe):
        flash('Classe não encontrada nesta campanha.', 'danger')
        return redirect(url_for('admin_classes_lista'))
    
    if request.method == 'POST':
        try:
            import json
            # Processa vantagens selecionadas (JSON do campo hidden)
            vantagens_json_str = request.form.get('vantagens_automaticas', '')
            vantagens_json = None
            if vantagens_json_str:
                try:
                    # Valida que é um JSON válido
                    ids = json.loads(vantagens_json_str)
                    if isinstance(ids, list) and len(ids) > 0:
                        vantagens_json = vantagens_json_str
                except:
                    pass
            
            # Processa perícias selecionadas (JSON do campo hidden)
            pericias_json_str = request.form.get('pericias_automaticas', '')
            pericias_json = None
            if pericias_json_str:
                try:
                    # Valida que é um JSON válido
                    ids = json.loads(pericias_json_str)
                    if isinstance(ids, list) and len(ids) > 0:
                        pericias_json = pericias_json_str
                except:
                    pass
            
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
                'vantagens_automaticas': vantagens_json,
                'pericias_automaticas': pericias_json,
                'observacoes': request.form.get('observacoes', ''),
                'is_active': request.form.get('is_active') == 'on'
            }
            
            Classe.atualizar(id, dados)
            flash('Classe atualizada com sucesso!', 'success')
            return redirect(url_for('admin_classes_lista'))
        except Exception as e:
            flash(f'Erro ao atualizar classe: {str(e)}', 'danger')
    
    # Carrega catálogos e parseia JSON das vantagens/perícias selecionadas
    import json
    vantagens = VantagemDesvantagemCatalogo.listar_vantagens()
    pericias = PericiaCatalogo.listar_todas()
    
    # Parseia IDs selecionados
    vantagens_selecionadas = []
    if classe.get('vantagens_automaticas'):
        try:
            vantagens_selecionadas = json.loads(classe['vantagens_automaticas'])
        except:
            vantagens_selecionadas = []
    
    pericias_selecionadas = []
    if classe.get('pericias_automaticas'):
        try:
            pericias_selecionadas = json.loads(classe['pericias_automaticas'])
        except:
            pericias_selecionadas = []
    
    return render_template('admin_classes_form.html', classe=classe, vantagens=vantagens, pericias=pericias,
                         vantagens_selecionadas=vantagens_selecionadas, pericias_selecionadas=pericias_selecionadas)

@app.route('/admin/classes/<int:id>/deletar', methods=['POST'])
def admin_classes_deletar(id):
    """Deleta uma classe (soft delete)"""
    if not verificar_admin():
        flash('Acesso restrito ao Mestre (admin).', 'danger')
        return redirect(url_for('admin_classes_lista'))

    if not pertence_a_campanha_ativa(Classe.buscar_por_id(id)):
        flash('Classe não encontrada nesta campanha.', 'danger')
        return redirect(url_for('admin_classes_lista'))
    
    try:
        Classe.deletar(id)
        flash('Classe deletada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao deletar classe: {str(e)}', 'danger')
    
    return redirect(url_for('admin_classes_lista'))

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000, use_reloader=True)

