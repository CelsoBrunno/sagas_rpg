# ==========================================
# Popula o catálogo de magias (GURPS 4e Módulo Básico)
# ==========================================
"""
Uso (na pasta sagas):
    python scripts/populate/magias_catalogo.py

Pode rodar de novo: magias com o mesmo nome são atualizadas.
"""

import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

for stream in ("stdout", "stderr"):
    try:
        getattr(sys, stream).reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from database import Database
from models import MagiaCatalogo
from magias_catalogo_dados import MAGIAS

CAMPOS = ('nome', 'escola', 'classe', 'dificuldade', 'custo', 'tempo', 'duracao',
          'pre_requisitos', 'pagina', 'descricao')


def main():
    Database.init_app(None, pool_size=1)
    for magia in MAGIAS:
        MagiaCatalogo.criar_ou_atualizar(dict(zip(CAMPOS, magia)))
    print(f"{len(MAGIAS)} magias no catálogo.")


if __name__ == '__main__':
    main()
