# ==========================================
# Carga, perícia e resumo do inventário
# ==========================================

from models import Atributos, Inventario
from utils.item_effects import enriquecer_inventario


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
