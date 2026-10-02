# ==========================================
# Popula a campanha Myth (ano 17) com raças, classes, locais e NPCs
# ==========================================
"""
Uso (na pasta sagas):
    python scripts/populate/myth_ano17.py

Pode rodar de novo: registros com o mesmo nome dentro da campanha são ignorados.
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
from models import Raca, Classe, Local, NPC
from myth_ano17_dados import RACAS, CLASSES, LOCAIS, NPCS

NOME_CAMPANHA = 'Myth'


def buscar_campanha_id():
    resultado = Database.execute_query(
        "SELECT id FROM campanhas WHERE nome_campanha = %s ORDER BY id LIMIT 1",
        (NOME_CAMPANHA,),
    )
    if not resultado:
        raise SystemExit(f"Campanha '{NOME_CAMPANHA}' não encontrada. Crie a campanha antes de rodar o script.")
    return resultado[0]['id']


def nomes_existentes(listagem):
    return {item['nome']: item['id'] for item in (listagem or [])}


def popular_catalogo(modelo, itens, campanha_id, rotulo):
    existentes = nomes_existentes(modelo.listar_por_campanha(campanha_id))
    for item in itens:
        if item['nome'] in existentes:
            print(f"  {rotulo} já existe: {item['nome']}")
            continue
        modelo.criar({**item, 'is_active': True, 'id_campanha': campanha_id})
        print(f"  {rotulo} criada: {item['nome']}")


def popular_locais(campanha_id):
    existentes = nomes_existentes(Local.listar_por_campanha(campanha_id))
    for local in LOCAIS:
        if local['nome'] in existentes:
            print(f"  Local já existe: {local['nome']}")
            continue
        existentes[local['nome']] = Local.criar({**local, 'id_campanha': campanha_id})
        print(f"  Local criado: {local['nome']}")
    return existentes


def popular_npcs(campanha_id, locais_por_nome):
    existentes = nomes_existentes(NPC.listar_por_campanha(campanha_id))
    for npc in NPCS:
        if npc['nome'] in existentes:
            print(f"  NPC já existe: {npc['nome']}")
            continue
        dados = {k: v for k, v in npc.items() if k != 'local'}
        dados['local_atual_id'] = locais_por_nome.get(npc['local']) if npc['local'] else None
        dados['id_campanha'] = campanha_id
        NPC.criar(dados)
        print(f"  NPC criado: {npc['nome']}")


def main():
    Database.init_app(None, pool_size=1)
    campanha_id = buscar_campanha_id()
    print(f"Campanha {NOME_CAMPANHA} (id {campanha_id})")
    print("Raças:")
    popular_catalogo(Raca, RACAS, campanha_id, 'Raça')
    print("Classes:")
    popular_catalogo(Classe, CLASSES, campanha_id, 'Classe')
    print("Locais:")
    locais_por_nome = popular_locais(campanha_id)
    print("NPCs:")
    popular_npcs(campanha_id, locais_por_nome)
    print("Pronto.")


if __name__ == '__main__':
    main()
