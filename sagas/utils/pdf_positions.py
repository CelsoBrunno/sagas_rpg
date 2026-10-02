# ==========================================
# Coordenadas dos Campos no PDF - Ficha GURPS
# ==========================================
"""
Este arquivo contém as coordenadas (X, Y) dos campos na ficha PDF.
O sistema de coordenadas do PDF começa do canto inferior esquerdo.

Para ajustar as posições:
1. Execute utils/find_st_position.py para gerar um PDF com grade
2. Abra o PDF gerado e identifique as coordenadas
3. Atualize os valores abaixo
"""

# Coordenadas dos Atributos Base
# Formato: {'campo': {'x': coordenada_x, 'y': coordenada_y, 'font_size': tamanho_fonte}}
POSICOES_ATRIBUTOS = {
    'ST': {
        'x': None,  # Será determinado visualmente
        'y': None,  # Será determinado visualmente  
        'font_size': 24,  # Tamanho da fonte (ajuste conforme necessário)
        'align': 'center'  # 'center', 'left', 'right'
    },
    'DX': {
        'x': None,
        'y': None,
        'font_size': 24,
        'align': 'center'
    },
    'IQ': {
        'x': None,
        'y': None,
        'font_size': 24,
        'align': 'center'
    },
    'HT': {
        'x': None,
        'y': None,
        'font_size': 24,
        'align': 'center'
    },
    'PV': {
        'x': None,
        'y': None,
        'font_size': 24,
        'align': 'center'
    },
    'PF': {
        'x': None,
        'y': None,
        'font_size': 24,
        'align': 'center'
    },
    'VB': {  # Velocidade Básica
        'x': None,
        'y': None,
        'font_size': 24,
        'align': 'center'
    },
    'DESLOCAMENTO': {
        'x': None,
        'y': None,
        'font_size': 24,
        'align': 'center'
    },
    'APARAR': {
        'x': None,
        'y': None,
        'font_size': 24,
        'align': 'center'
    },
    'BLOQUEIO': {
        'x': None,
        'y': None,
        'font_size': 24,
        'align': 'center'
    },
    'ESQUIVA': {
        'x': None,
        'y': None,
        'font_size': 24,
        'align': 'center'
    },
    'VONTADE': {
        'x': None,
        'y': None,
        'font_size': 24,
        'align': 'center'
    },
    'PERCEPCAO': {
        'x': None,
        'y': None,
        'font_size': 24,
        'align': 'center'
    },
    'GPD': {  # Golpe de Ponta
        'x': None,  # Usa POSICOES_ESTIMADAS se None
        'y': None,
        'font_size': 24,
        'align': 'center'
    },
    'BAL': {  # Golpe em Balanço
        'x': None,  # Usa POSICOES_ESTIMADAS se None
        'y': None,
        'font_size': 24,
        'align': 'center'
    },
    'RD': {  # Resistência a Dano
        'x': None,
        'y': None,
        'font_size': 24,
        'align': 'center'
    },
    'NOME': {  # Nome do personagem
        'x': None,
        'y': None,
        'font_size': 20,
        'align': 'left'
    },
    'RACA': {  # Raça do personagem
        'x': None,
        'y': None,
        'font_size': 20,
        'align': 'left'
    },
    'CLASSE': {  # Classe do personagem
        'x': None,
        'y': None,
        'font_size': 20,
        'align': 'left'
    },
    'USUARIO': {  # Nome do usuário/jogador
        'x': None,
        'y': None,
        'font_size': 18,
        'align': 'left'
    },
    'PONTOS_DISPONIVEIS': {  # Pontos disponíveis do usuário
        'x': None,
        'y': None,
        'font_size': 20,
        'align': 'center'
    }
}

# Valores padrão estimados (serão sobrescritos quando você encontrar as coordenadas corretas)
# Esses valores são exemplos e precisam ser ajustados
POSICOES_ESTIMADAS = {
    'ST': {'x': 135, 'y': 1153, 'font_size': 44, 'align': 'center'},
    'DX': {'x': 255, 'y': 1190, 'font_size': 44, 'align': 'center'},
    'IQ': {'x': 376, 'y': 1170, 'font_size': 44, 'align': 'center'},
    'HT': {'x': 471, 'y': 1096, 'font_size': 44, 'align': 'center'},
    'PV': {'x': 533, 'y': 992, 'font_size': 44 , 'align': 'center'},
    'PF': {'x': 535, 'y': 873, 'font_size': 44, 'align': 'center'},
    # Novos campos - coordenadas serão ajustadas visualmente
    'VB': {'x': 663, 'y': 1220, 'font_size': 44, 'align': 'center'},
    'DESLOCAMENTO': {'x': 663, 'y': 1132, 'font_size': 44, 'align': 'center'},
    'ESQUIVA': {'x': 663, 'y': 1045, 'font_size': 44, 'align': 'center'},
    'APARAR': {'x': 663, 'y': 958, 'font_size': 44, 'align': 'center'},
    'BLOQUEIO': {'x': 663, 'y': 872, 'font_size': 44, 'align': 'center'},   
    'VONTADE': {'x': 153, 'y': 750, 'font_size': 44, 'align': 'center'},
    'PERCEPCAO': {'x': 55, 'y': 750, 'font_size': 44, 'align': 'center'},
    'BAL': {'x': 663, 'y': 777, 'font_size': 44, 'align': 'center'},
    'GPD': {'x': 663, 'y': 690, 'font_size': 44, 'align': 'center'},
    'RD': {'x': 663, 'y': 524, 'font_size': 44, 'align': 'center'},  # Posição estimada - ajustar conforme necessário
    'NOME': {'x': 138, 'y': 1369, 'font_size': 28, 'align': 'left'},  # Posição estimada - ajustar conforme necessário
    'USUARIO': {'x': 335, 'y': 1369, 'font_size': 20, 'align': 'left'},  # Posição estimada - ajustar conforme necessário
    'RACA': {'x': 335, 'y': 1330, 'font_size': 24, 'align': 'left'},  # Posição estimada - ajustar conforme necessário
    'CLASSE': {'x': 138, 'y': 1330, 'font_size': 24, 'align': 'left'},  # Posição estimada - ajustar conforme necessário
    'PONTOS_DISPONIVEIS': {'x': 545, 'y': 1235 , 'font_size': 28, 'align': 'center'}  # Posição estimada - ajustar conforme necessário
}

# Coordenadas salvas (persistem durante a execução)
_posicoes_salvas = {}

def obter_posicao(campo, usar_estimativas=True):
    """
    Retorna a posição de um campo.
    
    Args:
        campo: Nome do campo ('ST', 'DX', 'IQ', 'HT', 'PV', 'PF', 'VB', 'DESLOCAMENTO', 'APARAR', 'BLOQUEIO', 'ESQUIVA', 'VONTADE', 'PERCEPCAO', 'GPD', 'BAL', 'RD', 'NOME', 'RACA', 'CLASSE', 'USUARIO', 'PONTOS_DISPONIVEIS')
        usar_estimativas: Se True, usa valores estimados quando coordenadas não estão definidas
    
    Returns:
        dict com 'x', 'y', 'font_size', 'align'
    """
    # Primeiro verifica se há posição salva
    if campo in _posicoes_salvas:
        return _posicoes_salvas[campo]
    
    # Depois verifica POSICOES_ATRIBUTOS
    posicao = POSICOES_ATRIBUTOS.get(campo)
    
    if not posicao or posicao['x'] is None:
        if usar_estimativas:
            return POSICOES_ESTIMADAS.get(campo, {'x': None, 'y': None, 'font_size': 24, 'align': 'center'})
        return {'x': None, 'y': None, 'font_size': 24, 'align': 'center'}
    
    return posicao

def atualizar_posicao(campo, x, y, font_size=24, align='center'):
    """
    Atualiza a posição de um campo (para uso em desenvolvimento/teste).
    Esta atualização persiste apenas durante a execução do script.
    """
    _posicoes_salvas[campo] = {
        'x': x,
        'y': y,
        'font_size': font_size,
        'align': align
    }
    POSICOES_ATRIBUTOS[campo] = _posicoes_salvas[campo]

