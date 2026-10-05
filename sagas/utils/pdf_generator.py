# ==========================================
# Sistema de Campanha GURPS - Gerador de PDF
# ==========================================
"""
Monta a ficha em PDF a partir dos dados do personagem.
O desenho sobre o template fica em utils/pdf_desenho.py.
"""

import os
from io import BytesIO

from utils.pdf_desenho import PDFRW_AVAILABLE, PdfReader, PdfWriter, adicionar_texto_sobre_pdf


def gerar_ficha_pdf_personagem(personagem_id, template_dir='static/templates', modo_teste=False):
    """
    Gera o PDF da ficha de personagem.
    
    Esta função deve ser chamada pelas rotas Flask após buscar
    todos os dados necessários do personagem.
    
    Args:
        personagem_id: ID do personagem
        template_dir: Diretório onde está o template PDF
    
    Returns:
        BytesIO com o PDF gerado
    
    Raises:
        FileNotFoundError: Se o template não existir
    """
    from models import Personagem, Atributos, VantagemDesvantagem, Pericia, Inventario
    
    # Busca dados do personagem
    personagem = Personagem.buscar_por_id(personagem_id)
    if not personagem:
        raise ValueError(f"Personagem {personagem_id} não encontrado")
    
    atributos = Atributos.buscar_por_personagem(personagem_id)
    vantagens = VantagemDesvantagem.listar_por_personagem(personagem_id)
    atributos_derivados = Atributos.calcular_atributos_derivados(atributos, vantagens) if atributos else {}

    if atributos:
        # Calcula DR (Resistência a Dano) - usa o mesmo método da rota ver_personagem
        from utils.item_effects import enriquecer_inventario
        inventario_bruto = Inventario.listar_por_personagem(personagem_id)
        bal_base = Atributos._calcular_golpe_balanco(atributos['ST'])
        gpd_base = Atributos._calcular_golpe_ponta(atributos['ST'])
        itens_enriquecidos, efeitos_itens = enriquecer_inventario(inventario_bruto, bal_base, gpd_base)
        bonus_itens = efeitos_itens.get('bonus', {}) if efeitos_itens else {}
        dr_adicional = bonus_itens.get('dr', 0)
        dr_base = atributos_derivados.get('dr_base', 0) or 0
        atributos_derivados['dr_base'] = dr_base
        atributos_derivados['dr_total'] = dr_base + dr_adicional
    
    # Dados auxiliares (podem ser usados futuramente para adicionar mais campos)
    vantagens = VantagemDesvantagem.listar_por_personagem(personagem_id)
    pericias = Pericia.listar_por_personagem(personagem_id)
    inventario = Inventario.listar_por_personagem(personagem_id)
    
    # Caminho do template - usa caminho absoluto baseado no diretório do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Tenta múltiplos caminhos possíveis
    template_paths = [
        os.path.join(base_dir, template_dir, 'ficha_personagem_template.pdf'),
        os.path.join(template_dir, 'ficha_personagem_template.pdf'),
        os.path.join(base_dir, 'static', 'templates', 'ficha_personagem_template.pdf'),
        'static/templates/ficha_personagem_template.pdf',
    ]
    
    template_path = None
    for path in template_paths:
        full_path = os.path.abspath(path) if not os.path.isabs(path) else path
        if os.path.exists(full_path) and os.path.isfile(full_path):
            template_path = full_path
            break
    
    if not template_path:
        error_msg = f"Template PDF não encontrado. Tentou os seguintes caminhos:\n"
        for path in template_paths:
            full_path = os.path.abspath(path) if not os.path.isabs(path) else path
            error_msg += f"  - {full_path}\n"
        error_msg += f"\nDiretório base: {base_dir}\n"
        error_msg += f"Certifique-se de que o arquivo 'ficha_personagem_template.pdf' existe em 'static/templates/'"
        raise FileNotFoundError(error_msg)
    
    # Modo teste: adiciona todos os atributos base nas posições corretas
    if modo_teste:
        from utils.pdf_positions import obter_posicao
        
        textos = []
        
        # Obtém dimensões da página para centralizar o texto de teste
        if not PDFRW_AVAILABLE:
            raise ImportError("pdfrw não está instalado. Execute: pip install pdfrw")
        template_pdf_temp = PdfReader(template_path)
        page_temp = template_pdf_temp.pages[0]
        mediabox_temp = page_temp.get('/MediaBox')
        if mediabox_temp and len(mediabox_temp) >= 4:
            page_width = float(mediabox_temp[2]) - float(mediabox_temp[0])
            page_height = float(mediabox_temp[3]) - float(mediabox_temp[1])
        else:
            page_width, page_height = 612, 792
        
        # Texto de teste removido
        
        # Lista de atributos base para adicionar
        atributos_base = ['ST', 'DX', 'IQ', 'HT']
        
        for atributo in atributos_base:
            # Obtém o valor do atributo
            if atributos:
                valor_atributo = str(atributos.get(atributo, 10))
            else:
                valor_atributo = '10'
            
            # Obtém a posição do atributo
            posicao = obter_posicao(atributo, usar_estimativas=True)
            
            # Se tiver coordenadas definidas, adiciona à lista
            if posicao['x'] is not None and posicao['y'] is not None:
                textos.append({
                    'texto': valor_atributo,
                    'x': posicao['x'],
                    'y': posicao['y'],
                    'font_size': posicao.get('font_size', 24),
                    'align': posicao.get('align', 'center'),
                    'atributo': 'INFO_MARROM'  # Atributos base também usam cor marrom
                })
        
        # Adiciona atributos derivados (PV e PF)
        atributos_derivados_campos = ['PV', 'PF']
        for campo in atributos_derivados_campos:
            # Obtém o valor do atributo derivado
            if atributos_derivados and campo in atributos_derivados:
                valor = str(atributos_derivados.get(campo))
            else:
                continue  # Pula se não tiver valor
            
            # Obtém a posição do campo
            posicao = obter_posicao(campo, usar_estimativas=True)
            
            # Se tiver coordenadas definidas, adiciona à lista
            if posicao['x'] is not None and posicao['y'] is not None:
                textos.append({
                    'texto': valor,
                    'x': posicao['x'],
                    'y': posicao['y'],
                    'font_size': posicao.get('font_size', 24),
                    'align': posicao.get('align', 'center'),
                    'atributo': campo  # Identifica o tipo de atributo para aplicar cor específica
                })
        
        # Adiciona novos campos derivados (VB, DESLOCAMENTO, APARAR, BLOQUEIO, ESQUIVA, VONTADE, PERCEPCAO, GPD, BAL, RD)
        # Mapeamento: campo_no_pdf -> chave_em_atributos_derivados
        campos_derivados_mapeados = {
            'VB': 'velocidade_basica',
            'DESLOCAMENTO': 'deslocamento',
            'APARAR': 'aparar',
            'BLOQUEIO': 'bloqueio',
            'ESQUIVA': 'esquiva',
            'VONTADE': 'vontade',
            'PERCEPCAO': 'percepcao',
            'GPD': 'gpd',
            'BAL': 'bal',
            'RD': 'dr_total'
        }
        
        for campo_pdf, chave_derivado in campos_derivados_mapeados.items():
            # Obtém o valor do atributo derivado
            if atributos_derivados and chave_derivado in atributos_derivados:
                valor = atributos_derivados[chave_derivado]
                # Formata valores decimais (ex: velocidade_basica = 5.5)
                if isinstance(valor, float):
                    valor_str = f"{valor:.1f}".rstrip('0').rstrip('.')
                else:
                    valor_str = str(valor)
            else:
                continue  # Pula se não tiver valor
            
            # Obtém a posição do campo
            posicao = obter_posicao(campo_pdf, usar_estimativas=True)
            
            # Se tiver coordenadas definidas, adiciona à lista
            if posicao['x'] is not None and posicao['y'] is not None:
                # Campos VB, DESLOCAMENTO, ESQUIVA, BLOQUEIO, APARAR, BAL, GPD usam cor marrom
                campos_marrom = ['VB', 'DESLOCAMENTO', 'ESQUIVA', 'BLOQUEIO', 'APARAR', 'BAL', 'GPD']
                atributo_tipo = 'INFO_MARROM' if campo_pdf in campos_marrom else None
                textos.append({
                    'texto': valor_str,
                    'x': posicao['x'],
                    'y': posicao['y'],
                    'font_size': posicao.get('font_size', 24),
                    'align': posicao.get('align', 'center'),
                    'atributo': atributo_tipo  # Marrom para campos específicos, dourado para outros
                })
        
        # Adiciona informações do personagem (nome, raça, classe, usuário, pontos)
        campos_info_personagem = {
            'NOME': personagem.get('nome', 'Sem nome'),
            'RACA': None,
            'CLASSE': None,
            'USUARIO': None,
            'PONTOS_DISPONIVEIS': None
        }
        
        # Busca raça
        if personagem.get('raca_id'):
            try:
                from models import Raca
                raca = Raca.buscar_por_id(personagem['raca_id'])
                if raca:
                    campos_info_personagem['RACA'] = raca.get('nome', 'Desconhecida')
            except:
                pass
        
        # Se não tiver raça_id, usa o campo raca (deprecated)
        if not campos_info_personagem['RACA']:
            campos_info_personagem['RACA'] = personagem.get('raca', 'Humano')
        
        # Busca classe
        if personagem.get('classe_id'):
            try:
                from models import Classe
                classe = Classe.buscar_por_id(personagem['classe_id'])
                if classe:
                    campos_info_personagem['CLASSE'] = classe.get('nome', 'Sem classe')
            except:
                pass
        
        # Busca usuário
        if personagem.get('id_usuario_jogador'):
            try:
                from models import Usuario
                usuario = Usuario.buscar_por_id(personagem['id_usuario_jogador'])
                if usuario:
                    # Prioriza nome_completo, senão username
                    campos_info_personagem['USUARIO'] = usuario.get('nome_completo') or usuario.get('username', 'Desconhecido')
                    # Busca pontos disponíveis do usuário
                    pontos_disponiveis = Usuario.get_pontos_disponiveis(personagem['id_usuario_jogador'])
                    campos_info_personagem['PONTOS_DISPONIVEIS'] = str(pontos_disponiveis) if pontos_disponiveis else '0'
            except:
                pass
        
        # Se não tiver usuário, usa jogador_nome (deprecated)
        if not campos_info_personagem['USUARIO']:
            campos_info_personagem['USUARIO'] = personagem.get('jogador_nome', 'NPC')
        
        # Adiciona campos de informação ao PDF
        # Campos de informação (NOME, USUARIO, RACA, CLASSE, PONTOS_DISPONIVEIS) usam cor marrom
        campos_info_marrom = ['NOME', 'USUARIO', 'RACA', 'CLASSE', 'PONTOS_DISPONIVEIS']
        for campo_pdf, valor in campos_info_personagem.items():
            if valor is None:
                continue
            
            posicao = obter_posicao(campo_pdf, usar_estimativas=True)
            if posicao['x'] is not None and posicao['y'] is not None:
                # Campos de informação usam cor marrom escura
                atributo_tipo = 'INFO_MARROM' if campo_pdf in campos_info_marrom else None
                textos.append({
                    'texto': str(valor),
                    'x': posicao['x'],
                    'y': posicao['y'],
                    'font_size': posicao.get('font_size', 24),
                    'align': posicao.get('align', 'left'),
                    'atributo': atributo_tipo  # Campos de informação terão cor marrom
                })
        
        # Se não houver textos (nenhuma posição definida), usa ST no centro como fallback
        if not textos:
            # Obtém dimensões para calcular centro
            if not PDFRW_AVAILABLE:
                raise ImportError("pdfrw não está instalado. Execute: pip install pdfrw")
            from pdfrw import PdfReader as PdfRwReader
            template_pdf_temp = PdfRwReader(template_path)
            page_temp = template_pdf_temp.pages[0]
            mediabox_temp = page_temp.get('/MediaBox')
            if mediabox_temp and len(mediabox_temp) >= 4:
                page_width = float(mediabox_temp[2]) - float(mediabox_temp[0])
                page_height = float(mediabox_temp[3]) - float(mediabox_temp[1])
            else:
                page_width, page_height = 612, 792
            
            st_valor = str(atributos.get('ST', 10) if atributos else 10)
            textos = [{
                'texto': st_valor,
                'x': page_width / 2,
                'y': page_height / 2,
                'font_size': 24,
                'align': 'center',
                'atributo': 'ST'  # Identifica como ST (dourado)
            }]
        
        pdf_buffer = adicionar_texto_sobre_pdf(template_path, textos)
        return pdf_buffer
    
    # Gera o PDF normalmente usando texto sobreposto
    # O template não tem campos de formulário, então desenhamos texto diretamente
    textos = []
    
    # Adiciona atributos base
    atributos_base = ['ST', 'DX', 'IQ', 'HT']
    for atributo in atributos_base:
        if atributos and atributo in atributos:
            valor = str(atributos[atributo])
            from utils.pdf_positions import obter_posicao
            posicao = obter_posicao(atributo, usar_estimativas=True)
            if posicao['x'] is not None and posicao['y'] is not None:
                textos.append({
                    'texto': valor,
                    'x': posicao['x'],
                    'y': posicao['y'],
                    'font_size': posicao.get('font_size', 24),
                    'align': posicao.get('align', 'center'),
                    'atributo': atributo  # Identifica o tipo de atributo para aplicar cor específica
                })
    
    # Adiciona atributos derivados (PV e PF)
    atributos_derivados_campos = ['PV', 'PF']
    for campo in atributos_derivados_campos:
        if atributos_derivados and campo in atributos_derivados:
            valor = str(atributos_derivados[campo])
            from utils.pdf_positions import obter_posicao
            posicao = obter_posicao(campo, usar_estimativas=True)
            if posicao['x'] is not None and posicao['y'] is not None:
                textos.append({
                    'texto': valor,
                    'x': posicao['x'],
                    'y': posicao['y'],
                    'font_size': posicao.get('font_size', 24),
                    'align': posicao.get('align', 'center'),
                    'atributo': campo  # Identifica o tipo de atributo para aplicar cor específica
                })
    
    # Adiciona novos campos derivados (VB, DESLOCAMENTO, APARAR, BLOQUEIO, ESQUIVA, VONTADE, PERCEPCAO, GPD, BAL)
    # Mapeamento: campo_no_pdf -> chave_em_atributos_derivados
    campos_derivados_mapeados = {
        'VB': 'velocidade_basica',
        'DESLOCAMENTO': 'deslocamento',
        'APARAR': 'aparar',
        'BLOQUEIO': 'bloqueio',
        'ESQUIVA': 'esquiva',
        'VONTADE': 'vontade',
        'PERCEPCAO': 'percepcao',
        'GPD': 'gpd',
        'BAL': 'bal'
    }
    
    for campo_pdf, chave_derivado in campos_derivados_mapeados.items():
        if atributos_derivados and chave_derivado in atributos_derivados:
            valor = atributos_derivados[chave_derivado]
            # Formata valores decimais (ex: velocidade_basica = 5.5)
            if isinstance(valor, float):
                valor_str = f"{valor:.1f}".rstrip('0').rstrip('.')
            else:
                valor_str = str(valor)
            
            from utils.pdf_positions import obter_posicao
            posicao = obter_posicao(campo_pdf, usar_estimativas=True)
            if posicao['x'] is not None and posicao['y'] is not None:
                # Campos VB, DESLOCAMENTO, ESQUIVA, BLOQUEIO, APARAR, BAL, GPD usam cor marrom
                campos_marrom = ['VB', 'DESLOCAMENTO', 'ESQUIVA', 'BLOQUEIO', 'APARAR', 'BAL', 'GPD']
                atributo_tipo = 'INFO_MARROM' if campo_pdf in campos_marrom else None
                textos.append({
                    'texto': valor_str,
                    'x': posicao['x'],
                    'y': posicao['y'],
                    'font_size': posicao.get('font_size', 24),
                    'align': posicao.get('align', 'center'),
                    'atributo': atributo_tipo  # Marrom para campos específicos, dourado para outros
                })
    
    # Gera PDF com textos sobrepostos
    if textos:
        pdf_buffer = adicionar_texto_sobre_pdf(template_path, textos)
    else:
        # Fallback: lê template sem modificações
        if not PDFRW_AVAILABLE:
            raise ImportError("pdfrw não está instalado. Execute: pip install pdfrw")
        template_pdf = PdfReader(template_path)
        pdf_buffer = BytesIO()
        writer = PdfWriter()
        writer.write(template_pdf, pdf_buffer)
        pdf_buffer.seek(0)
    
    return pdf_buffer

