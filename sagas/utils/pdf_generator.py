# ==========================================
# Sistema de Campanha GURPS - Gerador de PDF
# ==========================================
"""
Módulo responsável por gerar PDFs com texto sobreposto sobre templates
e dados dos personagens GURPS.

O template PDF deve estar localizado em:
    static/templates/ficha_personagem_template.pdf

O sistema desenha texto diretamente sobre o template usando coordenadas
definidas em utils/pdf_positions.py.
"""

import os
from io import BytesIO

# Importações opcionais - tentar importar apenas quando necessário
try:
    from pdfrw import PdfReader, PdfWriter
    PDFRW_AVAILABLE = True
except ImportError:
    PDFRW_AVAILABLE = False
    PdfReader = None
    PdfWriter = None

def _encontrar_fonte_mr_eaves():
    """
    Encontra o caminho da fonte Mr Eaves Small Caps.
    Retorna o caminho completo do arquivo ou None se não encontrar.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    font_paths = [
        # Tentativas OTF
        os.path.join(base_dir, 'static', 'fonts', 'Mr Eaves', 'Mr Eaves Small Caps.otf'),
        os.path.join(base_dir, 'static', 'fonts', 'Mr Eaves', 'MrEaves.otf'),
        # Tentativas TTF
        os.path.join(base_dir, 'static', 'fonts', 'Mr Eaves', 'Mr Eaves Small Caps.ttf'),
        os.path.join(base_dir, 'static', 'fonts', 'Mr Eaves', 'MrEaves.ttf'),
        # Caminhos relativos também
        'static/fonts/Mr Eaves/Mr Eaves Small Caps.otf',
        'static/fonts/Mr Eaves/Mr Eaves Small Caps.ttf',
    ]
    
    for font_path in font_paths:
        full_path = os.path.abspath(font_path) if not os.path.isabs(font_path) else font_path
        if os.path.exists(full_path):
            return full_path
    
    return None


def _registrar_fonte_mr_eaves_matplotlib():
    """
    Registra a fonte Mr Eaves usando Matplotlib (suporta PostScript).
    Retorna o objeto FontProperties ou None se não encontrar.
    """
    try:
        import matplotlib.font_manager as fm
        from matplotlib import ft2font
        
        font_path = _encontrar_fonte_mr_eaves()
        if font_path and os.path.exists(font_path):
            try:
                # Cria FontProperties com o caminho ABSOLUTO da fonte
                # Usar caminho absoluto garante que o Matplotlib encontre a fonte
                abs_font_path = os.path.abspath(font_path)
                font_prop = fm.FontProperties(fname=abs_font_path)
                
                # Testa se a fonte realmente funciona
                try:
                    import matplotlib.pyplot as plt
                    fig_test = plt.figure(figsize=(1, 1))
                    ax_test = fig_test.add_axes([0, 0, 1, 1])
                    ax_test.text(0.5, 0.5, 'A', fontproperties=font_prop, fontsize=12)
                    plt.close(fig_test)
                except Exception:
                    pass  # Fonte não renderiza, mas continua
                
                return font_prop
            except Exception:
                return None
        else:
            return None
    except ImportError:
        return None


def _registrar_fonte_mr_eaves_reportlab():
    """
    Tenta registrar a fonte Mr Eaves usando ReportLab (não suporta PostScript).
    Retorna o nome da fonte registrada ou None se falhar.
    """
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        fonte_nome = 'MrEaves'
        
        # Se já está registrada, retorna diretamente
        if fonte_nome in pdfmetrics.getRegisteredFontNames():
            return fonte_nome
        
        font_path = _encontrar_fonte_mr_eaves()
        if font_path and os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(fonte_nome, font_path))
                return fonte_nome
            except Exception as e:
                error_msg = str(e)
                if 'postscript outlines' in error_msg.lower():
                    return None  # Indica que precisa usar Matplotlib
                else:
                    return None
        return None
    except ImportError:
        return None


def adicionar_texto_sobre_pdf_matplotlib(template_path, textos_posicoes, font_size_padrao=48):
    """
    Adiciona textos sobre PDF usando Matplotlib (suporta fontes PostScript).
    """
    try:
        # Configura backend ANTES de importar pyplot
        import matplotlib
        matplotlib.use('Agg', force=True)  # Backend sem interface gráfica, força o uso
        
        # IMPORTANTE: Configura embedamento de fontes ANTES de criar qualquer figura
        # Isso garante que as fontes sejam embedadas no PDF gerado pelo Matplotlib
        matplotlib.rcParams['pdf.fonttype'] = 42  # TrueType (embeda fontes customizadas)
        matplotlib.rcParams['ps.fonttype'] = 42   # TrueType (embeda fontes customizadas)
        
        # Agora importa pyplot
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm
        from PyPDF2 import PdfReader as PyPdfReader, PdfWriter as PyPdfWriter
        
        # Fecha qualquer figura existente para evitar conflitos
        plt.close('all')
        
        # Obtém fonte
        font_prop = _registrar_fonte_mr_eaves_matplotlib()
        if not font_prop:
            # Fallback para fonte padrão
            font_prop = fm.FontProperties(family='sans-serif', weight='bold')
        
        # Lê template para obter dimensões
        if not PDFRW_AVAILABLE:
            raise ImportError("pdfrw não está instalado. Execute: pip install pdfrw")
        from pdfrw import PdfReader as PdfRwReader
        template_pdf = PdfRwReader(template_path)
        page = template_pdf.pages[0]
        mediabox = page.get('/MediaBox')
        
        if mediabox and len(mediabox) >= 4:
            page_width = float(mediabox[2]) - float(mediabox[0])
            page_height = float(mediabox[3]) - float(mediabox[1])
        else:
            page_width, page_height = 612, 792
        
        # Cria figura Matplotlib do tamanho exato da página
        # Remove todas as margens para evitar áreas pretas
        fig = plt.figure(figsize=(page_width/72, page_height/72), dpi=72, 
                        frameon=False)
        # Cria axes que ocupa toda a figura sem margens (esquerda, baixo, largura, altura)
        ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], frameon=False)
        ax.set_xlim(0, page_width)
        ax.set_ylim(0, page_height)
        ax.axis('off')
        
        # IMPORTANTE: Define fundo TRANSPARENTE para mesclagem correta
        # Áreas sem texto devem ser transparentes para não bloquear o template
        fig.patch.set_alpha(0.0)  # Transparente
        ax.patch.set_alpha(0.0)   # Transparente
        
        # Adiciona cada texto
        for item in textos_posicoes:
            texto = str(item.get('texto', ''))
            x = item.get('x')
            y = item.get('y')
            font_size = item.get('font_size', font_size_padrao)
            align = item.get('align', 'center')
            
            if x is None or y is None or not texto:
                continue
            
            # IMPORTANTE: Matplotlib usa origem no canto inferior esquerdo (como PDF)
            # A coordenada Y é medida de baixo para cima
            y_pos = y
            
            # Desenha texto conforme alinhamento
            # IMPORTANTE: A fonte "Mr Eaves Small Caps" já é small caps por padrão
            # Tenta recriar com caminho absoluto se necessário
            if not (hasattr(font_prop, '_file') and font_prop._file):
                font_path_temp = _encontrar_fonte_mr_eaves()
                if font_path_temp:
                    abs_path = os.path.abspath(font_path_temp)
                    font_prop = fm.FontProperties(fname=abs_path)
            
            # Identifica o tipo de atributo para aplicar cor específica
            atributo_tipo = (item.get('atributo') or '').upper()
            
            # Define cores baseado no tipo de atributo
            if atributo_tipo == 'PV':
                # Vermelho (paleta das bordas vermelhas)
                cor_principal = (0.75, 0.25, 0.25)  # Vermelho médio
                cor_highlight = (0.85, 0.35, 0.35)  # Vermelho claro (highlight)
            elif atributo_tipo == 'PF':
                # Azul (paleta das bordas azuis)
                cor_principal = (0.25, 0.35, 0.65)  # Azul médio
                cor_highlight = (0.35, 0.45, 0.75)  # Azul claro (highlight)
            elif atributo_tipo == 'CLASSE' or atributo_tipo == 'INFO_MARROM':
                # Marrom escuro para campos de informação (NOME, USUARIO, RACA, CLASSE)
                cor_principal = (0.45, 0.30, 0.20)  # Marrom escuro
                cor_highlight = (0.55, 0.40, 0.30)  # Marrom médio (highlight)
            else:
                # Padrão dourado para outros campos (campos derivados não especificados)
                cor_principal = (0.75, 0.65, 0.42)  # Dourado médio
                cor_highlight = (0.82, 0.72, 0.50)  # Dourado claro (highlight)
            
            # Offset para efeito de highlight (luz de cima-esquerda)
            offset_highlight = -1.0  # Highlight em cima-esquerda (negativo)
            
            # Renderiza em 2 camadas para criar efeito de gravado:
            # 1. Texto principal
            # 2. Highlight claro em cima-esquerda
            
            if align == 'center':
                # Texto principal
                ax.text(x, y_pos, texto, 
                       fontproperties=font_prop, fontsize=font_size,
                       ha='center', va='baseline', color=cor_principal, alpha=0.8)
                # Highlight claro (luz)
                ax.text(x + offset_highlight, y_pos - offset_highlight, texto,
                       fontproperties=font_prop, fontsize=font_size,
                       ha='center', va='baseline', color=cor_highlight, alpha=0.4)
            elif align == 'left':
                ax.text(x, y_pos, texto, 
                       fontproperties=font_prop, fontsize=font_size,
                       ha='left', va='baseline', color=cor_principal, alpha=0.8)
                ax.text(x + offset_highlight, y_pos - offset_highlight, texto,
                       fontproperties=font_prop, fontsize=font_size,
                       ha='left', va='baseline', color=cor_highlight, alpha=0.4)
            elif align == 'right':
                ax.text(x, y_pos, texto, 
                       fontproperties=font_prop, fontsize=font_size,
                       ha='right', va='baseline', color=cor_principal, alpha=0.8)
                ax.text(x + offset_highlight, y_pos - offset_highlight, texto,
                       fontproperties=font_prop, fontsize=font_size,
                       ha='right', va='baseline', color=cor_highlight, alpha=0.4)
        
        # Salva como PDF temporário
        # NOTA: rcParams já foi configurado no início da função para embedar fontes
        texto_pdf_buffer = BytesIO()
        try:
            # Salva com fundo TRANSPARENTE para mesclagem correta
            # Apenas o texto será visível sobre o template
            # bbox_inches=None mantém o tamanho exato da figura
            fig.savefig(texto_pdf_buffer, format='pdf', 
                       bbox_inches=None, pad_inches=0,
                       facecolor='none', edgecolor='none',
                       transparent=True, dpi=72)
            
            pdf_size = len(texto_pdf_buffer.getvalue())
        finally:
            plt.close(fig)
        texto_pdf_buffer.seek(0)
        
        # IMPORTANTE: PyPDF2 preserva melhor os recursos de fonte embedados pelo Matplotlib
        # pdfrw pode perder as fontes durante a mesclagem
        from PyPDF2 import PdfReader as PyPdfReader, PdfWriter as PyPdfWriter
        
        # Lê template e PDF de texto com PyPDF2
        template_reader = PyPdfReader(template_path)
        texto_pdf_buffer.seek(0)
        texto_reader = PyPdfReader(texto_pdf_buffer)
        
        # Cria writer para mesclar
        writer = PyPdfWriter()
        
        if template_reader.pages and texto_reader.pages:
            template_page = template_reader.pages[0]
            texto_page = texto_reader.pages[0]
            
            # IMPORTANTE: merge_page preserva recursos de fonte do PDF de texto
            # O texto vai SOBRE o template (ordem: template primeiro, texto depois)
            template_page.merge_page(texto_page)
            
            # Adiciona a página mesclada ao writer
            writer.add_page(template_page)
        
        output_buffer = BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)
        return output_buffer
        
    except ImportError:
        raise ImportError("Matplotlib não está instalado. Execute: pip install matplotlib")
    except Exception as e:
        print(f"Erro ao usar Matplotlib: {e}")
        import traceback
        traceback.print_exc()
        raise


def adicionar_texto_sobre_pdf(template_path, textos_posicoes, font_size_padrao=48):
    """
    Adiciona múltiplos textos sobre um PDF em posições específicas.
    Tenta usar ReportLab primeiro, se falhar por PostScript, usa Matplotlib.
    Todos os textos usam a fonte Mr Eaves Small Caps (ou Helvetica-Bold como fallback).
    
    Args:
        template_path: Caminho do template PDF
        textos_posicoes: Lista de dicts com {'texto': str, 'x': float, 'y': float, 'font_size': int, 'align': str}
        font_size_padrao: Tamanho de fonte padrão se não especificado
    
    Returns:
        BytesIO com o PDF mesclado
    """
    # Tenta primeiro com ReportLab
    fonte_reportlab = _registrar_fonte_mr_eaves_reportlab()
    
    if fonte_reportlab is None:
        # ReportLab não conseguiu (provavelmente PostScript), usa Matplotlib
        return adicionar_texto_sobre_pdf_matplotlib(template_path, textos_posicoes, font_size_padrao)
    
    if not PDFRW_AVAILABLE:
        raise ImportError("pdfrw não está instalado. Execute: pip install pdfrw")
    
    from reportlab.pdfgen import canvas
    from pdfrw import PdfReader, PdfWriter
    from io import BytesIO
    
    # Lê o PDF template
    template_pdf = PdfReader(template_path)
    
    if not template_pdf.pages:
        raise ValueError("PDF template sem paginas")
    
    # Obtém dimensões da página
    page = template_pdf.pages[0]
    mediabox = page.get('/MediaBox')
    
    if mediabox and len(mediabox) >= 4:
        page_width = float(mediabox[2]) - float(mediabox[0])
        page_height = float(mediabox[3]) - float(mediabox[1])
    else:
        page_width, page_height = 612, 792
    
    # Cria um PDF temporário com os textos
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(page_width, page_height))
    
    # Adiciona cada texto na posição especificada
    for item in textos_posicoes:
        texto = str(item.get('texto', ''))
        x = item.get('x')
        y = item.get('y')
        font_size = item.get('font_size', font_size_padrao)
        align = item.get('align', 'center')
        
        if x is None or y is None:
            continue
        
        can.setFont(fonte_reportlab, font_size)
        
        # Identifica o tipo de atributo para aplicar cor específica
        atributo_tipo = (item.get('atributo') or '').upper()
        
        # Define cores baseado no tipo de atributo
        if atributo_tipo == 'PV':
            # Vermelho (paleta das bordas vermelhas)
            cor_principal_r, cor_principal_g, cor_principal_b = 0.75, 0.25, 0.25  # Vermelho médio
            cor_highlight_r, cor_highlight_g, cor_highlight_b = 0.85, 0.35, 0.35  # Vermelho claro
        elif atributo_tipo == 'PF':
            # Azul (paleta das bordas azuis)
            cor_principal_r, cor_principal_g, cor_principal_b = 0.25, 0.35, 0.65  # Azul médio
            cor_highlight_r, cor_highlight_g, cor_highlight_b = 0.35, 0.45, 0.75  # Azul claro
        elif atributo_tipo == 'CLASSE' or atributo_tipo == 'INFO_MARROM':
            # Marrom escuro para campos de informação (NOME, USUARIO, RACA, CLASSE)
            cor_principal_r, cor_principal_g, cor_principal_b = 0.45, 0.30, 0.20  # Marrom escuro
            cor_highlight_r, cor_highlight_g, cor_highlight_b = 0.55, 0.40, 0.30  # Marrom médio (highlight)
        else:
            # Padrão dourado para outros campos (campos derivados não especificados)
            cor_principal_r, cor_principal_g, cor_principal_b = 0.75, 0.65, 0.42  # Dourado médio
            cor_highlight_r, cor_highlight_g, cor_highlight_b = 0.82, 0.72, 0.50  # Dourado claro
        
        # Offset para efeito de highlight (luz de cima-esquerda)
        offset_highlight = -1.0  # Highlight em cima-esquerda
        
        # Renderiza em 2 camadas para criar efeito de gravado:
        # 1. Texto principal
        can.setFillColorRGB(cor_principal_r, cor_principal_g, cor_principal_b)
        can.setFillAlpha(0.8)
        if align == 'center':
            can.drawCentredString(x, y, texto)
        elif align == 'left':
            can.drawString(x, y, texto)
        elif align == 'right':
            text_width = can.stringWidth(texto, fonte_reportlab, font_size)
            can.drawString(x - text_width, y, texto)
        
        # 2. Highlight claro (luz de cima-esquerda)
        can.setFillColorRGB(cor_highlight_r, cor_highlight_g, cor_highlight_b)
        can.setFillAlpha(0.4)
        if align == 'center':
            can.drawCentredString(x + offset_highlight, y - offset_highlight, texto)
        elif align == 'left':
            can.drawString(x + offset_highlight, y - offset_highlight, texto)
        elif align == 'right':
            text_width = can.stringWidth(texto, fonte_reportlab, font_size)
            can.drawString(x - text_width + offset_highlight, y - offset_highlight, texto)
    
    can.save()
    packet.seek(0)
    
    # Mescla o texto sobre o template usando PyPDF2
    from PyPDF2 import PdfReader as PyPdfReader, PdfWriter as PyPdfWriter
    
    with open(template_path, 'rb') as template_file:
        template_pypdf = PyPdfReader(template_file)
        texto_pypdf = PyPdfReader(packet)
        
        output_pdf = PyPdfWriter()
        
        for i in range(len(template_pypdf.pages)):
            page = template_pypdf.pages[i]
            if i < len(texto_pypdf.pages):
                page.merge_page(texto_pypdf.pages[i])
            output_pdf.add_page(page)
    
    output_buffer = BytesIO()
    output_pdf.write(output_buffer)
    output_buffer.seek(0)
    return output_buffer


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
    
    # Campos adicionais
    if atributos:
        # Percepção e Vontade (baseados em IQ + extras)
        percepcao_extra = atributos.get('percepcao_extra', 0) or 0
        vontade_extra = atributos.get('vontade_extra', 0) or 0
        atributos_derivados['percepcao'] = atributos['IQ'] + percepcao_extra
        atributos_derivados['vontade'] = atributos['IQ'] + vontade_extra
        atributos_derivados['deslocamento'] = int(atributos_derivados.get('velocidade_basica', 0))
        from config import Config
        bonus_aparar = atributos_derivados.get('bonus_aparar', 0)
        bonus_bloqueio = atributos_derivados.get('bonus_bloqueio', 0)
        atributos_derivados['aparar'] = int(atributos['DX'] / 2) + Config.APARAR_BASE + bonus_aparar
        atributos_derivados['bloqueio'] = Config.BLOQUEIO_BASE + bonus_bloqueio
        # Garante que esquiva está presente (já calculado em calcular_atributos_derivados)
        if 'esquiva' not in atributos_derivados:
            atributos_derivados['esquiva'] = int(atributos_derivados.get('velocidade_basica', 0)) + 3 + percepcao_extra
        
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

