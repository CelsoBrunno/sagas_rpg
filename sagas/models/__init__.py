# ==========================================
# Models Package - Sistema de Campanha GURPS
# ==========================================

"""
Módulo centralizado de models do sistema.

Importações recomendadas:
    from models import Personagem, Atributos, VantagemDesvantagem, Pericia
    from models import Campanha, Usuario, Local, NPC, Mapa, Imagem, Inventario
"""

# Models de Personagens
from .personagem import Personagem
from .atributos import Atributos
from .vantagem import VantagemDesvantagem
from .pericia import Pericia

# Models de Sistema
from .campanha import Campanha
from .usuario import Usuario
from .local import Local
from .npc import NPC
from .mapa import Mapa
from .imagem import Imagem
from .inventario import Inventario
from .equipamento import Equipamento
from .sessao import SessaoLog
from .pericia_catalogo import PericiaCatalogo
from .vantagem_desvantagem_catalogo import VantagemDesvantagemCatalogo
from .item_catalogo import ItemCatalogo
from .raca import Raca
from .classe import Classe
from .bestiario import Bestiario
from .magia import Magia, MagiaCatalogo

__all__ = [
    # Personagens
    'Personagem',
    'Atributos',
    'VantagemDesvantagem',
    'Pericia',
    # Sistema
    'Campanha',
    'Usuario',
    'Local',
    'NPC',
    'Mapa',
    'Imagem',
    'Inventario',
    'Equipamento',
    'SessaoLog',
    'PericiaCatalogo',
    'VantagemDesvantagemCatalogo',
    'ItemCatalogo',
    # Raças e Classes
    'Raca',
    'Classe',
    'Bestiario',
    'Magia',
    'MagiaCatalogo'
]

