# ==========================================
# Sistema de Campanha GURPS - Gerador de PDF
# ==========================================
"""
Desenha texto sobre o PDF modelo da ficha.
A montagem dos dados do personagem fica em pdf_generator.py.

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
