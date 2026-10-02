# ==========================================
# Popula a campanha Myth (ano 17) com raças, classes, locais, NPCs,
# bestiário e as perícias/itens de Myth nos catálogos GURPS
# ==========================================
"""
Uso (na pasta sagas):
    python scripts/populate/populate_world_data.py --catalogo   # catálogos GURPS genéricos (uma vez)
    python scripts/populate/myth_ano17.py

Pode rodar de novo: registros com o mesmo nome dentro da campanha são ignorados.
Perícias e itens de catálogo são atualizados pelo nome. No bestiário, textos e foto
das criaturas existentes são atualizados (nível de revelação e ficha não mudam).
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
from models import Raca, Classe, Local, NPC, PericiaCatalogo, ItemCatalogo, Bestiario
from myth_ano17_dados import RACAS, CLASSES, LOCAIS, NPCS
from myth_esquadra_dados import NPCS_ESQUADRA
from myth_catalogo_dados import PERICIAS, ITENS
from myth_bestiario_dados import CRIATURAS
from fichas_npc import criar_personagem_completo

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
    for npc in NPCS + NPCS_ESQUADRA:
        if npc['nome'] in existentes:
            print(f"  NPC já existe: {npc['nome']}")
            continue
        dados = {k: v for k, v in npc.items() if k != 'local'}
        dados['local_atual_id'] = locais_por_nome.get(npc['local']) if npc['local'] else None
        dados['id_campanha'] = campanha_id
        NPC.criar(dados)
        print(f"  NPC criado: {npc['nome']}")


def atualizar_lore(existente, criatura):
    """Sincroniza textos e foto; nível de revelação e ficha GURPS ficam como o mestre deixou."""
    Bestiario.atualizar(existente['id'], {
        **existente,
        'categoria': criatura['categoria'],
        'descricao_publica': criatura['descricao_publica'],
        'descricao_mestre': criatura['descricao_mestre'],
        'imagem_url': criatura.get('imagem_url') or existente['imagem_url'],
    })
    if existente['ficha_personagem_id']:
        Database.execute_query(
            "UPDATE personagens SET biografia = %s WHERE id = %s",
            (criatura['descricao_publica'], existente['ficha_personagem_id']),
            fetch=False,
        )
    sincronizar_galeria(existente['id'], criatura)


def sincronizar_galeria(criatura_id, criatura):
    cadastradas = {img['imagem_url'] for img in Bestiario.listar_imagens(criatura_id)}
    for imagem_url in criatura.get('galeria', []):
        if imagem_url not in cadastradas:
            Bestiario.adicionar_imagem(criatura_id, imagem_url)


def popular_bestiario(campanha_id):
    existentes = {c['nome']: c for c in (Bestiario.listar_por_campanha(campanha_id) or [])}
    for criatura in CRIATURAS:
        if criatura['nome'] in existentes:
            atualizar_lore(existentes[criatura['nome']], criatura)
            print(f"  Criatura já existe, lore atualizada: {criatura['nome']}")
            continue
        ficha_id = criar_personagem_completo({
            **criatura['ficha'],
            'nome': criatura['nome'],
            'raca': criatura['nome'],
            'categoria': 'Criatura',
            'biografia': criatura['descricao_publica'],
            'id_campanha': campanha_id,
        })
        novo_id = Bestiario.criar({
            'id_campanha': campanha_id,
            'nome': criatura['nome'],
            'categoria': criatura['categoria'],
            'descricao_publica': criatura['descricao_publica'],
            'descricao_mestre': criatura['descricao_mestre'],
            'imagem_url': criatura.get('imagem_url'),
            'ficha_personagem_id': ficha_id,
            'nivel_revelacao': Bestiario.OCULTA,
        })
        sincronizar_galeria(novo_id, criatura)
        print(f"  Criatura criada (oculta): {criatura['nome']}")


def popular_catalogos_gurps():
    for pericia in PERICIAS:
        PericiaCatalogo.criar_se_nao_existir(**pericia)
        print(f"  Perícia: {pericia['nome']}")
    for item in ITENS:
        ItemCatalogo.criar_se_nao_existir(**item)
        print(f"  Item: {item['nome']}")


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
    print("Catálogos GURPS (perícias e itens de Myth):")
    popular_catalogos_gurps()
    print("Bestiário:")
    popular_bestiario(campanha_id)
    print("Pronto.")


if __name__ == '__main__':
    main()
