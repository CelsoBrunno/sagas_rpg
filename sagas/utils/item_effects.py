# ==========================================
# Utilitário de Efeitos de Itens (GURPS)
# ==========================================

"""
Centraliza o mapeamento de itens do inventário para seus efeitos mecânicos.
Os valores são aproximados com base em referências comuns do GURPS 4ª edição
e podem ser ajustados conforme a mesa evolui.

Estrutura de cada entrada:
    {
        'categoria': 'Armadura' | 'Arma' | 'Acessório' | ...,
        'bonus': {
            'dr': int,                 # Bônus de Defesa (Resistência a Dano)
            'dano_corte': int,         # Bônus em dano de corte (swing)
            'dano_perf': int,          # Bônus em dano perfurante (thrust)
            'aparar': int,             # Bônus em Aparar
            'bloqueio': int,           # Bônus em Bloqueio
            'esquiva': int,            # Bônus/penalidade em Esquiva
            'st': int, 'dx': int, 'iq': int, 'ht': int,
            'per': int, 'will': int,
        },
        'efeitos': [
            'Descrições textuais dos efeitos'
        ]
    }

Para itens não mapeados, tentamos gerar um efeito genérico com base no nome
ou retornamos apenas as notas salvas pelo Mestre/Jogador.
"""

import re
from collections import defaultdict
from typing import Dict, List, Tuple, Any, Optional


ITEM_EFFECTS: Dict[str, Dict[str, Any]] = {
    # Armaduras
    'armadura de couro': {
        'categoria': 'Armadura',
        'bonus': {'dr': 2, 'esquiva': -1},
        'efeitos': [
            'RD +2 (torso e braços)',
            'Penalidade -1 em Esquiva por peso'
        ]
    },
    'armadura de guardião': {
        'categoria': 'Armadura',
        'bonus': {'dr': 5, 'bloqueio': 1},
        'efeitos': [
            'RD +5 (corpo completo)',
            '+1 em Bloqueio por ombreiras reforçadas'
        ]
    },
    'armadura de cavaleiro da aliança': {
        'categoria': 'Armadura',
        'bonus': {'dr': 7, 'esquiva': -2, 'aparar': 1},
        'efeitos': [
            'RD +7 (corpo completo)',
            'Penalidade -2 de Esquiva (armadura pesada)',
            '+1 em Aparar com armas de haste (ombros balanceados)'
        ]
    },
    'armadura de general': {
        'categoria': 'Armadura',
        'bonus': {'dr': 6, 'bloqueio': 1},
        'efeitos': [
            'RD +6 (corpo completo)',
            '+1 em Bloqueio com escudos pela geometria reforçada'
        ]
    },
    'armadura real': {
        'categoria': 'Armadura',
        'bonus': {'dr': 6, 'aparar': 1},
        'efeitos': [
            'RD +6 com proteção completa',
            '+1 em Aparar (balanceada para cerimônias de duelo)'
        ]
    },
    'armadura negra': {
        'categoria': 'Armadura',
        'bonus': {'dr': 8, 'esquiva': -2},
        'efeitos': [
            'RD +8 (proteção pesada)',
            'Penalidade -2 em Esquiva (peso considerável)'
        ]
    },
    'armadura de couro com reforço': {
        'categoria': 'Armadura',
        'bonus': {'dr': 3, 'esquiva': -1},
        'efeitos': [
            'RD +3 (placas leves adicionais)',
            'Penalidade -1 em Esquiva'
        ]
    },

    # Armas brancas
    'espada império': {
        'categoria': 'Arma',
        'bonus': {'dano_corte': 2, 'aparar': 1},
        'efeitos': [
            'Dano de Corte +2 (swing)',
            '+1 em Aparar ao utilizar esta espada'
        ]
    },
    'espada imperial': {
        'categoria': 'Arma',
        'bonus': {'dano_corte': 2, 'dano_perf': 1},
        'efeitos': [
            'Dano de Corte +2 (swing)',
            'Dano Perfurante +1 (thrust)'
        ]
    },
    'espada real': {
        'categoria': 'Arma',
        'bonus': {'dano_corte': 1},
        'efeitos': ['Dano de Corte +1 (swing)']
    },
    'espada do general': {
        'categoria': 'Arma',
        'bonus': {'dano_corte': 2, 'aparar': 1},
        'efeitos': [
            'Dano de Corte +2 (swing)',
            '+1 em Aparar'
        ]
    },
    'espada rebeliao': {
        'categoria': 'Arma',
        'bonus': {'dano_corte': 3},
        'efeitos': [
            'Dano de Corte +3 (swing)',
            'Ignora 1 ponto de RD contra alvos opressores'
        ]
    },
    'espada negra': {
        'categoria': 'Arma',
        'bonus': {'dano_corte': 3, 'dano_perf': 2},
        'efeitos': [
            'Dano de Corte +3 (swing)',
            'Dano Perfurante +2 (thrust)',
            'Ataques causam medo em falhas de Vontade'
        ]
    },
    'espada protetora': {
        'categoria': 'Arma',
        'bonus': {'dano_corte': 1, 'aparar': 1, 'bloqueio': 1},
        'efeitos': [
            'Dano de Corte +1',
            '+1 em Aparar e Bloqueio ao canalizar magia de Luz'
        ]
    },
    'espada curta': {
        'categoria': 'Arma',
        'bonus': {'dano_corte': 1},
        'efeitos': ['Dano de Corte +1 (arma leve)']
    },
    'espada curta de mitril': {
        'categoria': 'Arma',
        'bonus': {'dano_corte': 1, 'aparar': 1},
        'efeitos': [
            'Dano de Corte +1',
            '+1 em Aparar (material extremamente leve)'
        ]
    },

    # Arcos e armas à distância
    'arco dreicans': {
        'categoria': 'Arma à Distância',
        'bonus': {'dano_perf': 2, 'per': 1},
        'efeitos': [
            'Dano Perfurante +2 (flechas)',
            '+1 em testes de Percepção para rastrear alvos marcados'
        ]
    },
    'aljava': {
        'categoria': 'Acessório',
        'bonus': {},
        'efeitos': ['Armazena 20 flechas, recarga rápida (-1 turno)']
    },

    # Foco mágico / cajados / grimórios
    'cajado mágico': {
        'categoria': 'Foco Mágico',
        'bonus': {'iq': 1, 'aparar': 1},
        'efeitos': [
            '+1 em rolagens de Magia',
            'Pode aparar ataques de energia com +1'
        ]
    },
    'cajado de madeira': {
        'categoria': 'Foco Mágico',
        'bonus': {'iq': 1},
        'efeitos': ['+1 em Magia quando usado como foco']
    },
    'cajado necromântico': {
        'categoria': 'Foco Mágico',
        'bonus': {'iq': 1, 'will': 1},
        'efeitos': [
            '+1 em Magias de Necromancia',
            '+1 em testes de Vontade contra medo'
        ]
    },
    'cajado de aprendiz': {
        'categoria': 'Foco Mágico',
        'bonus': {'iq': 1},
        'efeitos': ['+1 em Magia (somente escolas básicas)']
    },
    'cetro laminado': {
        'categoria': 'Foco Mágico',
        'bonus': {'iq': 1, 'dano_corte': 1},
        'efeitos': [
            '+1 em Magias ritualísticas',
            'Causa dano cortante mínimo (thr+1) em contato'
        ]
    },
    'grimório mágico': {
        'categoria': 'Acessório',
        'bonus': {'iq': 1},
        'efeitos': ['+1 em Magias pesquisadas neste grimório']
    },
    'grimório de dinzentis': {
        'categoria': 'Acessório',
        'bonus': {'iq': 1, 'per': 1},
        'efeitos': [
            '+1 em Magias de Luz e Trevas',
            '+1 em testes de Percepção para identificar magia antiga'
        ]
    },

    # Acessórios mágicos
    'bracelete dourado': {
        'categoria': 'Acessório',
        'bonus': {'will': 1, 'esquiva': 1},
        'efeitos': [
            '+1 em Vontade contra magia',
            '+1 em Esquiva enquanto estiver brilhando'
        ]
    },
    'manopla do dragão negro': {
        'categoria': 'Acessório',
        'bonus': {'st': 2, 'dano_corte': 1},
        'efeitos': [
            '+2 em ST (apenas para testes de força pura)',
            '+1 em dano de Corte (golpes desarmados com garras sombrias)',
            'Atrai a atenção do Dragão Negro'
        ]
    },
    'manopla direita de walchor': {
        'categoria': 'Acessório',
        'bonus': {'st': 1, 'aparar': 1},
        'efeitos': [
            '+1 em ST ao agarrar',
            '+1 em Aparar com armas de uma mão'
        ]
    },
    'manto e capuz': {
        'categoria': 'Vestuário',
        'bonus': {'per': 1},
        'efeitos': [
            '+1 em testes de Furtividade em ambientes urbanos',
            '+1 em Percepção para resistir a ofuscamento'
        ]
    },
    'vestes élficas negras': {
        'categoria': 'Vestuário',
        'bonus': {'per': 1, 'esquiva': 1},
        'efeitos': [
            '+1 em Furtividade',
            '+1 em Esquiva (vestes leves de combate)'
        ]
    },
    'coroa real': {
        'categoria': 'Acessório',
        'bonus': {'will': 1},
        'efeitos': [
            '+1 em Reputação em domínios aliados',
            '+1 em testes de Vontade contra intriga política'
        ]
    },
    'coroa imperial': {
        'categoria': 'Acessório',
        'bonus': {'will': 1, 'per': 1},
        'efeitos': [
            '+1 em Reputação em todo império',
            '+1 em Percepção para detectar mentira em audiências'
        ]
    },
    'bússola do dragão': {
        'categoria': 'Acessório',
        'bonus': {'per': 1},
        'efeitos': [
            '+1 em Percepção para rastrear seres dracônicos',
            'Sempre aponta para a ameaça dracônica mais próxima'
        ]
    },
    'três dados de seis faces': {
        'categoria': 'Miscelânea',
        'bonus': {},
        'efeitos': ['Pode rolar novamente uma falha simples por sessão (sorte do jogador)']
    },
}


_EQUIPAMENTO_CATEGORIAS = {
    'armas corpo-a-corpo',
    'armas à distância',
    'armas a distancia',
    'escudos',
    'armaduras',
    'vestuário',
    'vestuario',
    'foco mágico',
    'foco magico',
    'focos mágicos',
    'focos magicos',
    'acessórios',
    'acessorios',
    'acessórios mágicos',
    'acessorios magicos',
    'ferramentas e kits',
    'montarias e veículos',
    'montarias e veiculos',
    'exploração',
    'exploracao'
}

_CONSUMIVEL_CATEGORIAS = {
    'consumíveis',
    'consumiveis'
}


def _normalizar_nome(nome: str) -> str:
    return (nome or '').strip().lower()


def _inferir_tipo_item(categoria: str, nome: str) -> str:
    cat = _normalizar_nome(categoria)
    if cat in _CONSUMIVEL_CATEGORIAS:
        return 'consumivel'
    if cat in _EQUIPAMENTO_CATEGORIAS:
        return 'equipamento'

    nome_norm = _normalizar_nome(nome)
    if any(substr in nome_norm for substr in ['poção', 'pocao', 'antídoto', 'antidoto', 'ração', 'racao', 'flecha', 'munição', 'municao']):
        return 'consumivel'
    if any(substr in nome_norm for substr in ['armadura', 'armas', 'escudo', 'espada', 'lança', 'lanca', 'adaga', 'machado', 'martelo', 'besta', 'arco', 'foco', 'grimório', 'grimorio', 'bracelete', 'amuleto', 'cajado', 'kit', 'ferramenta', 'mochila', 'cinturão', 'cinturao', 'aljava', 'vestes']):
        return 'equipamento'
    return 'outro'


def _gerar_efeitos_genericos(nome: str, notas: str = None) -> Dict[str, Any]:
    """Tenta gerar efeitos genéricos a partir de palavras-chave."""
    nome_lower = _normalizar_nome(nome)
    efeitos: List[str] = []
    bonus: Dict[str, int] = {}
    categoria = 'Miscelânea'

    if any(token in nome_lower for token in ['armadura', 'couraça', 'couraca']):
        categoria = 'Armaduras'
        bonus.setdefault('dr', 3)
        bonus.setdefault('esquiva', -1)
        efeitos.append('Armadura genérica: RD +3, penalidade -1 em Esquiva')

    if any(token in nome_lower for token in ['espada', 'lâmina', 'lamina', 'machado', 'maça', 'maca', 'martelo', 'lança', 'lanca']):
        categoria = 'Armas Corpo-a-Corpo'
        bonus.setdefault('dano_corte', 1)
        efeitos.append('Arma branca: dano de corte +1 (estimativa)')

    if any(token in nome_lower for token in ['cajado', 'cetro', 'orbe', 'grimório', 'grimorio']):
        categoria = 'Focos Mágicos'
        bonus.setdefault('iq', 1)
        efeitos.append('Foco mágico: +1 em testes de Magia')

    if any(token in nome_lower for token in ['manto', 'capuz', 'vestes', 'uniforme', 'roupa']):
        categoria = 'Vestuário'
        bonus.setdefault('per', 1)
        efeitos.append('Vestuário furtivo/resistente: ajuste em Percepção conforme contexto')

    if 'manopla' in nome_lower or 'luva' in nome_lower:
        categoria = 'Acessórios'
        bonus.setdefault('st', 1)
        efeitos.append('Força adicional: +1 em testes de ST')

    if any(token in nome_lower for token in ['mochila', 'cinturão', 'cinturao', 'aljava']):
        categoria = 'Acessórios'
        efeitos.append('Equipamento de suporte para transporte de itens')

    if any(token in nome_lower for token in ['coroa', 'bracelete', 'amuleto', 'bússola', 'bussola', 'dados']):
        categoria = 'Acessórios Mágicos'
        bonus.setdefault('will', 1)
        efeitos.append('Presença marcante: +1 em Vontade/Reputação')

    if 'escudo' in nome_lower:
        categoria = 'Escudos'
        bonus.setdefault('bloqueio', 1)
        efeitos.append('Escudo padrão: DB +1 (estimativa)')

    if any(token in nome_lower for token in ['arco', 'besta', 'funda', 'flecha', 'projétil', 'projetil', 'balestra']):
        categoria = 'Armas à Distância'
        bonus.setdefault('dano_perf', 1)
        efeitos.append('Ataque à distância: dano perfurante +1 (estimativa)')

    if any(token in nome_lower for token in ['poção', 'pocao', 'antídoto', 'antidoto', 'ração', 'racao', 'elixir']):
        categoria = 'Consumíveis'
        efeitos.append('Consumível: efeito imediato conforme descrição')

    if 'kit' in nome_lower or 'ferramenta' in nome_lower:
        categoria = 'Ferramentas e Kits'
        efeitos.append('Ferramenta especializada: aplica bônus conforme a perícia relacionada')

    if any(token in nome_lower for token in ['cavalo', 'carroça', 'carroca', 'carruagem']):
        categoria = 'Montarias e Veículos'
        efeitos.append('Meio de transporte: consulte regras de carga e deslocamento')

    if any(token in nome_lower for token in ['tenda', 'corda', 'tocha', 'lanterna', 'escalada']):
        categoria = 'Exploração'
        efeitos.append('Equipamento de exploração: auxilia testes de Sobrevivência e Escalada')

    if notas:
        efeitos.append(notas)

    if not efeitos:
        efeitos = [notas] if notas else ['Efeitos não catalogados']

    return {
        'categoria': categoria,
        'bonus': bonus,
        'efeitos': efeitos
    }


def obter_efeitos_item(nome: str, notas: str = None) -> Dict[str, Any]:
    """Retorna os efeitos conhecidos para um item específico."""
    chave = _normalizar_nome(nome)
    dados = ITEM_EFFECTS.get(chave)
    if not dados:
        return _gerar_efeitos_genericos(nome, notas)

    efeitos = list(dados.get('efeitos', []))
    if notas and notas not in efeitos:
        efeitos.append(notas)

    return {
        'categoria': dados.get('categoria', 'Miscelânea'),
        'bonus': dict(dados.get('bonus', {})),
        'efeitos': efeitos
    }


_DANO_REGEX = re.compile(r'^\s*(?P<dados>\d+)d(?:(?P<sinal>[+-])(?P<valor>\d+))?\s*$')


def _resolver_modificador(valor: Any) -> int:
    if valor is None:
        return 0
    try:
        return int(valor)
    except (TypeError, ValueError):
        return 0


def _aplicar_modificador_dano(base_expr: Optional[str], modificador: Optional[int]) -> Optional[str]:
    if not base_expr:
        return None
    base_expr = base_expr.strip()
    mod = _resolver_modificador(modificador)
    if mod == 0:
        return base_expr

    match = _DANO_REGEX.match(base_expr)
    if not match:
        sufixo = f'+{mod}' if mod > 0 else f'{mod}'
        return f'{base_expr}{sufixo}'

    dados = int(match.group('dados'))
    base_mod = 0
    sinal = match.group('sinal')
    valor = match.group('valor')
    if sinal and valor:
        base_mod = int(valor)
        if sinal == '-':
            base_mod *= -1

    total = base_mod + mod
    if total == 0:
        sufixo = ''
    elif total > 0:
        sufixo = f'+{total}'
    else:
        sufixo = f'{total}'

    return f'{dados}d{sufixo}'


def _formata_dano_com_tipo(expressao: Optional[str], tipo: Optional[str]) -> Optional[str]:
    if not expressao:
        return None
    tipo = (tipo or '').strip()
    if tipo:
        return f'{expressao} ({tipo})'
    return expressao


def _formatar_resumo_danos(danos_ativos: List[Dict[str, Any]]) -> List[str]:
    linhas: List[str] = []
    for dano in danos_ativos:
        partes: List[str] = []
        if dano.get('dano_bal'):
            partes.append(f"Bal {dano['dano_bal']}")
        if dano.get('dano_gdp'):
            partes.append(f"GdP {dano['dano_gdp']}")
        if not partes:
            continue
        slot = dano.get('slot')
        slot_txt = f" [{slot}]" if slot else ''
        linhas.append(f"{dano.get('nome')}{slot_txt}: " + " | ".join(partes))
    return linhas


def _slots_disponiveis_para_categoria(categoria: str, nome: str) -> List[str]:
    categoria_lower = (categoria or '').lower()
    nome_lower = (nome or '').lower()

    slots: List[str] = []

    if any(token in categoria_lower for token in ['arma', 'foco']):
        slots = ['mao_direita', 'mao_esquerda']

    if 'escudo' in categoria_lower or 'escudo' in nome_lower:
        slots = ['mao_direita', 'mao_esquerda']

    if 'armadura' in categoria_lower:
        slots = ['armadura']

    if 'vestuário' in categoria_lower or 'vestuario' in categoria_lower:
        slots = ['vestimenta']

    if any(token in categoria_lower for token in ['acessório', 'acessorio']):
        slots = ['acessorio']

    if 'consum' in categoria_lower or 'montaria' in categoria_lower or 'veículo' in categoria_lower or 'veiculo' in categoria_lower:
        return []

    if not slots:
        if any(token in categoria_lower for token in ['exploração', 'exploracao']):
            return []
        if any(token in categoria_lower for token in ['ferramenta', 'kit']):
            return []

    return slots


def enriquecer_inventario(
    itens: List[Dict[str, Any]],
    bal_base: Optional[str] = None,
    gpd_base: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Retorna itens enriquecidos com efeitos e um resumo agregado."""
    resumo_bonus = defaultdict(int)
    observacoes: List[str] = []
    danos_ativos: List[Dict[str, Any]] = []

    itens_enriquecidos: List[Dict[str, Any]] = []
    for item in itens:
        efeitos_info = obter_efeitos_item(item.get('nome_item'), item.get('notas'))

        enriched = dict(item)
        categoria_efeitos = efeitos_info.get('categoria')
        enriched['categoria'] = categoria_efeitos or item.get('categoria') or 'Miscelânea'
        enriched['efeitos'] = efeitos_info.get('efeitos')
        enriched['slot'] = item.get('slot_equipado')
        enriched['slots_disponiveis'] = _slots_disponiveis_para_categoria(enriched['categoria'], item.get('nome_item'))
        enriched['tipo_item'] = item.get('tipo_item') or _inferir_tipo_item(enriched['categoria'], item.get('nome_item'))

        dano_bal_mod = _resolver_modificador(item.get('dano_bal_mod'))
        dano_bal_tipo = item.get('dano_bal_tipo')
        dano_gdp_mod = _resolver_modificador(item.get('dano_gdp_mod'))
        dano_gdp_tipo = item.get('dano_gdp_tipo')
        rd_mod = _resolver_modificador(item.get('rd_mod'))
        rd_tipo = item.get('rd_tipo')

        enriched['dano_bal_mod'] = dano_bal_mod
        enriched['dano_bal_tipo'] = dano_bal_tipo
        enriched['dano_gdp_mod'] = dano_gdp_mod
        enriched['dano_gdp_tipo'] = dano_gdp_tipo
        enriched['rd_mod'] = rd_mod
        enriched['rd_tipo'] = rd_tipo

        if bal_base:
            enriched['dano_bal_base'] = bal_base
            dano_bal_final = _aplicar_modificador_dano(bal_base, dano_bal_mod)
            enriched['dano_bal_final'] = _formata_dano_com_tipo(dano_bal_final, dano_bal_tipo)
        if gpd_base:
            enriched['dano_gdp_base'] = gpd_base
            dano_gdp_final = _aplicar_modificador_dano(gpd_base, dano_gdp_mod)
            enriched['dano_gdp_final'] = _formata_dano_com_tipo(dano_gdp_final, dano_gdp_tipo)

        itens_enriquecidos.append(enriched)

        if enriched.get('slot'):
            # Se o item tem RD definido no catálogo, não aplica RD genérico dos efeitos
            # O RD do catálogo tem prioridade
            bonus_efeitos = dict(efeitos_info.get('bonus', {}))
            if rd_mod and rd_mod > 0:
                # Remove RD genérico se houver, pois o RD do catálogo tem prioridade
                bonus_efeitos.pop('dr', None)
            
            for chave, valor in bonus_efeitos.items():
                resumo_bonus[chave] += valor
            
            # Adiciona RD do item se houver (será formatado no resumo_bonus)
            if rd_mod and rd_mod > 0:
                resumo_bonus['dr'] = resumo_bonus.get('dr', 0) + rd_mod
            
            observacoes.extend(efeitos_info.get('efeitos', []))

            if enriched.get('dano_bal_final') or enriched.get('dano_gdp_final'):
                danos_ativos.append({
                    'item_id': enriched.get('id'),
                    'nome': enriched.get('nome_item'),
                    'slot': enriched.get('slot'),
                    'dano_bal': enriched.get('dano_bal_final'),
                    'dano_gdp': enriched.get('dano_gdp_final'),
                    'dano_bal_mod': dano_bal_mod,
                    'dano_gdp_mod': dano_gdp_mod
                })

    # Coleta itens com RD para resumo
    itens_com_rd = []
    rd_total = 0
    for item in itens_enriquecidos:
        if item.get('slot') and item.get('rd_mod') and item.get('rd_mod') > 0:
            rd_item = item.get('rd_mod', 0)
            rd_total += rd_item
            itens_com_rd.append({
                'item_id': item.get('id'),
                'nome': item.get('nome_item'),
                'slot': item.get('slot'),
                'rd_mod': rd_item,
                'rd_tipo': item.get('rd_tipo')
            })

    resumo_textual = _formatar_resumo_bonus(resumo_bonus)
    resumo_textual.extend(_formatar_resumo_danos(danos_ativos))

    melhor_dano_bal = max(
        (d for d in danos_ativos if d.get('dano_bal')),
        key=lambda d: d.get('dano_bal_mod', 0),
        default=None
    )
    melhor_dano_gdp = max(
        (d for d in danos_ativos if d.get('dano_gdp')),
        key=lambda d: d.get('dano_gdp_mod', 0),
        default=None
    )

    bal_mod_val = melhor_dano_bal.get('dano_bal_mod') if melhor_dano_bal else None
    gdp_mod_val = melhor_dano_gdp.get('dano_gdp_mod') if melhor_dano_gdp else None

    return itens_enriquecidos, {
        'bonus': dict(resumo_bonus),
        'observacoes': observacoes,
        'resumo_textual': resumo_textual,
        'danos': danos_ativos,
        'rd': itens_com_rd,
        'rd_total': rd_total,
        'danos_base': {
            'bal': bal_base,
            'gdp': gpd_base
        },
        'dano_em_uso': {
            'bal': melhor_dano_bal.get('dano_bal') if melhor_dano_bal else None,
            'bal_item': melhor_dano_bal.get('nome') if melhor_dano_bal else None,
            'bal_mod': bal_mod_val if bal_mod_val not in (None, 0) else None,
            'gdp': melhor_dano_gdp.get('dano_gdp') if melhor_dano_gdp else None,
            'gdp_item': melhor_dano_gdp.get('nome') if melhor_dano_gdp else None,
            'gdp_mod': gdp_mod_val if gdp_mod_val not in (None, 0) else None
        }
    }


def _formatar_resumo_bonus(bonus: Dict[str, int]) -> List[str]:
    """Converte o dicionário de bônus em mensagens amigáveis."""
    textos: List[str] = []

    if not bonus:
        return ['Nenhum efeito ativo catalogado.']

    mapping = {
        'dr': 'RD total +{valor}',
        'esquiva': 'Esquiva {sinal}{valor}',
        'aparar': 'Aparar +{valor}',
        'bloqueio': 'Bloqueio +{valor}',
        'dano_corte': 'Dano de corte +{valor}',
        'dano_perf': 'Dano perfurante +{valor}',
        'st': 'ST +{valor}',
        'dx': 'DX +{valor}',
        'iq': 'IQ +{valor}',
        'ht': 'HT +{valor}',
        'per': 'Percepção +{valor}',
        'will': 'Vontade +{valor}'
    }

    for chave, texto in mapping.items():
        if chave in bonus and bonus[chave] != 0:
            valor = bonus[chave]
            sinal = '+' if valor > 0 else ''
            textos.append(texto.format(valor=valor, sinal=sinal))

    if not textos:
        textos.append('Itens equipados não conferem bônus numéricos registrados.')

    return textos

