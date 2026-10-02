# ==========================================
# Script de Preenchimento do Mundo
# Sistema de Campanha GURPS
# ==========================================

"""
Script para preencher o banco de dados com dados do mundo.

Uso:
    python populate_world_data.py

Funcionalidades:
    - Popular catálogos GURPS (perícias, vantagens e desvantagens)
    - Criar dados de exemplo (usuários, personagens, locais, NPCs, mapas)
    - Preencher dados do mundo (locais, personagens, NPCs)

Estrutura esperada dos dados:
    - Locais: lista de dicionários com nome, tipo, descricao_publica, descricao_mestre
    - Personagens: lista de dicionários com nome, raca, categoria, atributos, vantagens, pericias, inventario
    - NPCs: lista de dicionários vinculando personagens a locais
"""

import base64
import json
import os
import sys
import zlib

from flask import Flask

# Garante que o diretório raiz do projeto esteja no PYTHONPATH
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

for stream in ("stdout", "stderr"):
    try:
        getattr(sys, stream).reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
from database import Database
from config import Config
from models import (
    Personagem, Atributos, VantagemDesvantagem, Pericia,
    Local, NPC, Inventario, Usuario, Mapa,
    VantagemDesvantagemCatalogo, ItemCatalogo, PericiaCatalogo
)
from fichas_npc import classificar_tipo_item, criar_personagem_completo

# Cria uma instância Flask mínima para inicializar o Database
app = Flask(__name__)
app.config.from_object(Config)

# Inicializa o pool de conexões com tamanho 1 para scripts (PythonAnywhere tem limite de 6 conexões)
Database.init_app(app, pool_size=1)

print(f"Conectando ao banco: {Config.MYSQL_DB} em {Config.MYSQL_HOST}")

def criar_local(dados_local):
    """Cria um local no banco de dados"""
    try:
        local_id = Local.criar(dados_local)
        print(f"✅ Local criado: {dados_local['nome']} (ID: {local_id})")
        return local_id
    except Exception as e:
        print(f"❌ Erro ao criar local {dados_local['nome']}: {str(e)}")
        return None

def criar_npc(dados_npc, locais_dict, personagens_dict):
    """
    Cria um NPC vinculando um personagem a um local
    
    Estrutura esperada:
    {
        'nome': str,
        'personagem_nome': str,  # Nome do personagem criado
        'local_nome': str ou None,  # Nome do local (pode ser None)
        'descricao_breve': str (opcional),
        'descricao_completa': str (opcional),
        'status': str (opcional, padrão 'Vivo')
    }
    """
    try:
        personagem_id = personagens_dict.get(dados_npc['personagem_nome'])
        local_nome = dados_npc.get('local_nome')
        local_id = locais_dict.get(local_nome) if local_nome else None
        
        if not personagem_id:
            print(f"❌ Personagem '{dados_npc['personagem_nome']}' não encontrado para NPC {dados_npc['nome']}")
            return None
        
        # Se local_nome foi fornecido mas não encontrado, avisa mas continua
        if local_nome and not local_id:
            print(f"⚠️  Local '{local_nome}' não encontrado para NPC {dados_npc['nome']}. NPC será criado sem local.")
        
        dados_npc_db = {
            'nome': dados_npc['nome'],
            'status': dados_npc.get('status', 'Vivo'),
            'descricao_breve': dados_npc.get('descricao_breve', ''),
            'descricao_completa': dados_npc.get('descricao_completa', ''),
            'imagem_url': None,
            'local_atual_id': local_id,  # Pode ser None
            'ficha_personagem_id': personagem_id
        }
        
        npc_id = NPC.criar(dados_npc_db)
        print(f"✅ NPC criado: {dados_npc['nome']} (ID: {npc_id})")
        return npc_id
        
    except Exception as e:
        print(f"❌ Erro ao criar NPC {dados_npc.get('nome', 'Desconhecido')}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def processar_dados_mundo(dados_mundo):
    """
    Processa dados completos do mundo
    
    Estrutura esperada:
    {
        'locais': [...],
        'personagens': [...],
        'npcs': [...]
    }
    """
    print("=" * 60)
    print("🌍 PREENCHENDO DADOS DO MUNDO")
    print("=" * 60)
    
    # Dicionários para mapear nomes para IDs
    locais_dict = {}
    personagens_dict = {}
    
    # 1. Criar locais
    print("\n📍 Criando locais...")
    locais = dados_mundo.get('locais', [])
    for local_data in locais:
        local_id = criar_local(local_data)
        if local_id:
            locais_dict[local_data['nome']] = local_id
    
    # 2. Criar personagens
    print("\n👤 Criando personagens...")
    personagens = dados_mundo.get('personagens', [])
    for personagem_data in personagens:
        personagem_id = criar_personagem_completo(personagem_data)
        if personagem_id:
            personagens_dict[personagem_data['nome']] = personagem_id
    
    # 3. Criar NPCs (vincular personagens a locais)
    print("\n🎭 Criando NPCs...")
    npcs = dados_mundo.get('npcs', [])
    for npc_data in npcs:
        criar_npc(npc_data, locais_dict, personagens_dict)
    
    print("\n" + "=" * 60)
    print("✅ PREENCHIMENTO CONCLUÍDO!")
    print("=" * 60)
    print(f"Locais criados: {len(locais_dict)}")
    print(f"Personagens criados: {len(personagens_dict)}")
    print(f"NPCs criados: {len(npcs)}")

def popular_catalogo_pericias():
    """Popula o catálogo de perícias com base nas regras do GURPS 4ª edição."""
    print("\n" + "=" * 60)
    print("📘 POPULANDO CATÁLOGO DE PERÍCIAS")
    print("=" * 60)

    existentes = {p['nome'].lower(): p for p in (PericiaCatalogo.listar_todas() or [])}
    adicionadas = 0
    atualizadas = 0

    pericias = [
        ("Acrobacia", "DX", "D", "DX-3 [1]; DX-2 [2]; DX-1 [4]; DX [8]", "Saltos mortais, rolamentos, recuperar equilíbrio em quedas."),
        ("Atletismo", "DX", "M", "DX-5 [1]; DX-4 [2]; DX-3 [4]; DX-2 [8]; DX-1 [12]; DX [16]", "Combina corrida, salto e escalada para tarefas atléticas amplas."),
        ("Arco", "DX", "D", "DX-5 [1]; DX-4 [2]; DX-3 [4]; DX-2 [8]; DX-1 [12]; DX [16]", "Disparo com arcos tradicionais, longo alcance e tiro tático."),
        ("Arremesso", "DX", "M", "DX-4 [1]; DX-3 [2]; DX-2 [4]; DX-1 [8]; DX [12]", "Lançar objetos improvisados com precisão."),
        ("Armadilhas", "IQ", "D", "IQ-6 [1]; IQ-5 [2]; IQ-4 [4]; IQ-3 [8]; IQ-2 [12]; IQ-1 [16]; IQ [20]", "Configurar, detectar e desarmar armadilhas mecânicas simples."),
        ("Arqueologia", "IQ", "D", "IQ-6 [1]; IQ-5 [2]; IQ-4 [4]; IQ-3 [8]; IQ-2 [12]; IQ-1 [16]; IQ [20]", "Estudo de culturas antigas, escavações e interpretação de artefatos."),
        ("Avaliação", "IQ", "M", "IQ-5 [1]; IQ-4 [2]; IQ-3 [4]; IQ-2 [8]; IQ-1 [12]; IQ [16]", "Determinar o valor de itens, tesouros ou mercadorias."),
        ("Biologia", "IQ", "D", "IQ-6 [1]; IQ-5 [2]; IQ-4 [4]; IQ-3 [8]; IQ-2 [12]; IQ-1 [16]; IQ [20]", "Conhecimento de ecossistemas, anatomia básica e classificação de seres vivos."),
        ("Briga", "DX", "F", "DX-4 [1]; DX-3 [2]; DX-2 [4]; DX-1 [8]; DX [12]", "Combate desarmado básico; socos, joelhadas e cabeçadas."),
        ("Camuflagem", "IQ", "F", "IQ-3 [1]; IQ-2 [2]; IQ-1 [4]; IQ [8]", "Esconder pessoas, objetos ou trilhas em ambientes naturais."),
        ("Cartografia", "IQ", "M", "IQ-5 [1]; IQ-4 [2]; IQ-3 [4]; IQ-2 [8]; IQ-1 [12]; IQ [16]", "Criação e leitura de mapas, interpretação de coordenadas."),
        ("Contabilidade", "IQ", "D", "IQ-6 [1]; IQ-5 [2]; IQ-4 [4]; IQ-3 [8]; IQ-2 [12]; IQ-1 [16]; IQ [20]", "Manter livros-caixa, detectar fraudes e planejar finanças."),
        ("Diplomacia", "IQ", "VD", "IQ-6 [1]; IQ-5 [2]; IQ-4 [4]; IQ-3 [8]; IQ-2 [12]; IQ-1 [16]; IQ [20]; IQ+1 [24]", "Negociações formais, acordos de paz e resolução de conflitos."),
        ("Disfarce", "IQ", "M", "IQ-5 [1]; IQ-4 [2]; IQ-3 [4]; IQ-2 [8]; IQ-1 [12]; IQ [16]", "Alterar aparência, criar identidades falsas e maquiagem teatral."),
        ("Eletrônica", "IQ", "D", "IQ-6 [1]; IQ-5 [2]; IQ-4 [4]; IQ-3 [8]; IQ-2 [12]; IQ-1 [16]; IQ [20]", "Projetar, reparar e analisar circuitos eletrônicos."),
        ("Escalada", "DX", "M", "DX-4 [1]; DX-3 [2]; DX-2 [4]; DX-1 [8]; DX [12]", "Subir superfícies rochosas, árvores e estruturas artificiais."),
        ("Escrita", "IQ", "F", "IQ-3 [1]; IQ-2 [2]; IQ-1 [4]; IQ [8]", "Produzir textos claros, caligrafia legível e linguagem formal."),
        ("Esquiva Acrobática", "DX", "D", "DX-3 [1]; DX-2 [2]; DX-1 [4]; DX [8]", "Desvios elaborados durante combate corpo a corpo."),
        ("Etiqueta", "IQ", "F", "IQ-3 [1]; IQ-2 [2]; IQ-1 [4]; IQ [8]", "Conhecimento dos costumes sociais para não ofender anfitriões."),
        ("Falsificação", "IQ", "D", "IQ-6 [1]; IQ-5 [2]; IQ-4 [4]; IQ-3 [8]; IQ-2 [12]; IQ-1 [16]; IQ [20]", "Criar documentos ilegais, moeda falsa e assinaturas perfeitas."),
        ("Furtividade", "DX", "M", "DX-4 [1]; DX-3 [2]; DX-2 [4]; DX-1 [8]; DX [12]", "Mover-se silenciosamente, evitar detecção e aproximar-se de alvos."),
        ("Herbologia", "IQ", "M", "IQ-5 [1]; IQ-4 [2]; IQ-3 [4]; IQ-2 [8]; IQ-1 [12]; IQ [16]", "Identificar plantas, criar remédios simples e venenos naturais."),
        ("História", "IQ", "M", "IQ-5 [1]; IQ-4 [2]; IQ-3 [4]; IQ-2 [8]; IQ-1 [12]; IQ [16]", "Contextualizar eventos históricos, culturas e líderes importantes."),
        ("Intimidação", "IQ", "F", "IQ-3 [1]; IQ-2 [2]; IQ-1 [4]; IQ [8]", "Coagir, ameaçar e assustar alvos; usa Vontade (derivada de IQ) como base."),
        ("Investigação", "IQ", "D", "IQ-6 [1]; IQ-5 [2]; IQ-4 [4]; IQ-3 [8]; IQ-2 [12]; IQ-1 [16]; IQ [20]", "Coletar pistas, analisar cenas e interrogar testemunhas."),
        ("Jogos de Azar", "IQ", "F", "IQ-3 [1]; IQ-2 [2]; IQ-1 [4]; IQ [8]", "Entendimento de probabilidades, blefe e jogos de cartas ou dados."),
        ("Liderança", "IQ", "M", "IQ-5 [1]; IQ-4 [2]; IQ-3 [4]; IQ-2 [8]; IQ-1 [12]; IQ [16]", "Inspirar aliados, coordenar grupos e delegar ordens sob pressão."),
        ("Medicina", "IQ", "VD", "IQ-6 [1]; IQ-5 [2]; IQ-4 [4]; IQ-3 [8]; IQ-2 [12]; IQ-1 [16]; IQ [20]; IQ+1 [24]", "Diagnóstico, cirurgias complexas e tratamento prolongado de pacientes."),
        ("Natação", "HT", "F", "HT-3 [1]; HT-2 [2]; HT-1 [4]; HT [8]", "Manter-se em flutuação, mergulhar e nadar longas distâncias."),
        ("Navegação (Terrestre)", "IQ", "M", "IQ-5 [1]; IQ-4 [2]; IQ-3 [4]; IQ-2 [8]; IQ-1 [12]; IQ [16]", "Orientação por mapas, estrelas e marcos naturais."),
        ("Primeiros Socorros", "IQ", "F", "IQ-3 [1]; IQ-2 [2]; IQ-1 [4]; IQ [8]", "Estancar sangramentos, reanimar feridos e estabilizar pacientes."),
        ("Psicologia", "IQ", "D", "IQ-6 [1]; IQ-5 [2]; IQ-4 [4]; IQ-3 [8]; IQ-2 [12]; IQ-1 [16]; IQ [20]", "Analisar comportamento, detectar mentiras e tratar traumas leves."),
        ("Rastreio", "IQ", "M", "IQ-5 [1]; IQ-4 [2]; IQ-3 [4]; IQ-2 [8]; IQ-1 [12]; IQ [16]", "Seguir rastros, interpretar pegadas e sinais deixados por criaturas."),
        ("Sobrevivência (Floresta)", "IQ", "M", "IQ-5 [1]; IQ-4 [2]; IQ-3 [4]; IQ-2 [8]; IQ-1 [12]; IQ [16]", "Encontrar abrigo, comida e água em ambientes florestais (usa Percepção derivada de IQ)."),
        ("Sobrevivência (Deserto)", "IQ", "M", "IQ-5 [1]; IQ-4 [2]; IQ-3 [4]; IQ-2 [8]; IQ-1 [12]; IQ [16]", "Lidar com calor extremo, escassez de água e tempestades de areia (usa Percepção derivada de IQ)."),
        ("Sobrevivência (Montanha)", "IQ", "M", "IQ-5 [1]; IQ-4 [2]; IQ-3 [4]; IQ-2 [8]; IQ-1 [12]; IQ [16]", "Escalar, lidar com frio intenso e preparar acampamentos em altitude (usa Percepção derivada de IQ)."),
        ("Tática", "IQ", "D", "IQ-6 [1]; IQ-5 [2]; IQ-4 [4]; IQ-3 [8]; IQ-2 [12]; IQ-1 [16]; IQ [20]", "Planejar combates, posicionar tropas e prever manobras inimigas."),
        ("Uso de Escudo", "DX", "F", "DX-3 [1]; DX-2 [2]; DX-1 [4]; DX [8]", "Bloquear ataques com escudos de diferentes tamanhos."),
        ("Uso de Lança", "DX", "M", "DX-4 [1]; DX-3 [2]; DX-2 [4]; DX-1 [8]; DX [12]", "Empunhar lanças em combate corpo a corpo ou com estoques."),
    ]

    for nome, atributo, dificuldade, custo_texto, descricao in pericias:
        ja_existia = nome.lower() in existentes
        PericiaCatalogo.criar_se_nao_existir(
            nome=nome,
            atributo_base=atributo,
            dificuldade=dificuldade,
            custo_texto=custo_texto,
            descricao=descricao
        )
        if ja_existia:
            atualizadas += 1
            status = "Atualizado"
        else:
            adicionadas += 1
            status = "Adicionado"
            existentes[nome.lower()] = True
        print(f"✓ {status}: {nome} ({atributo}/{dificuldade})")

    total = len(pericias)
    print(f"\n✅ Catálogo de perícias disponível: {total} entradas (novas: {adicionadas}, atualizadas: {atualizadas})")


def popular_catalogo_itens():
    """Popula o catálogo de itens usados pelo inventário."""
    print("\n" + "=" * 60)
    print("🛡️ POPULANDO CATÁLOGO DE ITENS")
    print("=" * 60)

    itens_catalogo = [
        # Armas Corpo-a-Corpo
        {
            "nome": "Espada Longa",
            "categoria": "Armas Corpo-a-Corpo",
            "preco": 500,
            "peso": 3.0,
            "descricao": "Dano: sw+1 corte / thr+1 perfurante. Alcance: C,1. Perícia recomendada: Espada Curta/Broadsword.",
            "dano_bal_mod": 1,
            "dano_bal_tipo": "corte",
            "dano_gdp_mod": 1,
            "dano_gdp_tipo": "perfurante"
        },
        {
            "nome": "Machado de Batalha",
            "categoria": "Armas Corpo-a-Corpo",
            "preco": 90,
            "peso": 4.0,
            "descricao": "Dano: sw+2 corte. Alcance: 1. Requer perícia Machado/Two-Handed Axe.",
            "dano_bal_mod": 2,
            "dano_bal_tipo": "corte"
        },
        {
            "nome": "Lança Curta",
            "categoria": "Armas Corpo-a-Corpo",
            "preco": 40,
            "peso": 4.0,
            "descricao": "Dano: thr+2 perfurante. Alcance: 1,2 (impulso). Pode ser arremessada (alcance x1.5).",
            "dano_gdp_mod": 2,
            "dano_gdp_tipo": "perfurante"
        },
        {
            "nome": "Adaga de Aço",
            "categoria": "Armas Corpo-a-Corpo",
            "preco": 20,
            "peso": 1.0,
            "descricao": "Dano: thr corte/perfurante. Alcance: C. Arremesso alcance x0.5.",
            "dano_gdp_mod": 0,
            "dano_gdp_tipo": "corte/perfurante"
        },
        {
            "nome": "Maça de Guerra",
            "categoria": "Armas Corpo-a-Corpo",
            "preco": 80,
            "peso": 5.0,
            "descricao": "Dano: sw+3 contusão. Alcance: 1. Perícia recomendada: Maça.",
            "dano_bal_mod": 3,
            "dano_bal_tipo": "contusão"
        },
        {
            "nome": "Martelo Pesado",
            "categoria": "Armas Corpo-a-Corpo",
            "preco": 65,
            "peso": 5.0,
            "descricao": "Dano: sw+3 contusão. Alcance: 1. Excelente contra obstáculos e armaduras.",
            "dano_bal_mod": 3,
            "dano_bal_tipo": "contusão"
        },

        # Armas À Distância
        {
            "nome": "Arco Longo",
            "categoria": "Armas à Distância",
            "preco": 200,
            "peso": 3.0,
            "descricao": "Dano: thr+2 perfurante. Alcance: 15/20. 2 turnos para preparar uma flecha.",
            "dano_gdp_mod": 2,
            "dano_gdp_tipo": "perfurante"
        },
        {
            "nome": "Arco Composto",
            "categoria": "Armas à Distância",
            "preco": 600,
            "peso": 3.5,
            "descricao": "Dano: thr+3 perfurante. Alcance: 18/24. Reduz penalidades de vento em -1.",
            "dano_gdp_mod": 3,
            "dano_gdp_tipo": "perfurante"
        },
        {
            "nome": "Besta Leve",
            "categoria": "Armas à Distância",
            "preco": 150,
            "peso": 6.0,
            "descricao": "Dano: thr+4 perfurante. Alcance: 12/18. Tempo de recarga padrão: 4 turnos.",
            "dano_gdp_mod": 4,
            "dano_gdp_tipo": "perfurante"
        },
        {
            "nome": "Besta Pesada",
            "categoria": "Armas à Distância",
            "preco": 250,
            "peso": 7.0,
            "descricao": "Dano: thr+6 perfurante. Alcance: 15/21. Tempo de recarga 6 turnos sem auxílio.",
            "dano_gdp_mod": 6,
            "dano_gdp_tipo": "perfurante"
        },
        {
            "nome": "Funda de Couro",
            "categoria": "Armas à Distância",
            "preco": 10,
            "peso": 1.0,
            "descricao": "Dano: thr+1 contusão (pedra). Alcance: 12/24. Necessita munição.",
            "dano_gdp_mod": 1,
            "dano_gdp_tipo": "contusão"
        },
        {
            "nome": "Machadinha de Arremesso",
            "categoria": "Armas à Distância",
            "preco": 40,
            "peso": 2.0,
            "descricao": "Dano: sw+2 corte. Alcance x1. Arremesso equilibrado para retorno.",
            "dano_bal_mod": 2,
            "dano_bal_tipo": "corte"
        },

        # Escudos
        {
            "nome": "Escudo Pequeno",
            "categoria": "Escudos",
            "preco": 40,
            "peso": 7.0,
            "descricao": "DB +1. Peso inclui empunhadura. Penalidade -1 para certas perícias finas."
        },
        {
            "nome": "Escudo Médio",
            "categoria": "Escudos",
            "preco": 60,
            "peso": 15.0,
            "descricao": "DB +2. Oferece cobertura parcial. Requer perícia Uso de Escudo."
        },
        {
            "nome": "Escudo Grande",
            "categoria": "Escudos",
            "preco": 90,
            "peso": 25.0,
            "descricao": "DB +3. Cobertura ampla, porém impõe -1 em ataques em ambientes estreitos."
        },

        # Armaduras
        {
            "nome": "Couraça de Couro Rígido",
            "categoria": "Armaduras",
            "preco": 150,
            "peso": 10.0,
            "descricao": "RD 2 no torso e braços. Penalidade de Esquiva -1. Ideal para batedores."
        },
        {
            "nome": "Cota de Malha Completa",
            "categoria": "Armaduras",
            "preco": 300,
            "peso": 18.0,
            "descricao": "RD 4 em torso e membros. Esquiva -1; reduz ruído em -2 com acolchoamento."
        },
        {
            "nome": "Corselete Laminado",
            "categoria": "Armaduras",
            "preco": 600,
            "peso": 26.0,
            "descricao": "RD 5 em torso, ombros e coxas. Esquiva -2. Resistência a impacto."
        },
        {
            "nome": "Armadura de Placas Completa",
            "categoria": "Armaduras",
            "preco": 5000,
            "peso": 45.0,
            "descricao": "RD 7 corpo inteiro. Esquiva -2; requer ajuda para vestir."
        },

        # Vestuário e Fardamentos
        {
            "nome": "Traje de Camuflagem Florestal",
            "categoria": "Vestuário",
            "preco": 150,
            "peso": 4.0,
            "descricao": "+2 em Furtividade em ambientes de floresta. Penalidade em áreas urbanas."
        },
        {
            "nome": "Vestes Nobres Cerimoniais",
            "categoria": "Vestuário",
            "preco": 1000,
            "peso": 6.0,
            "descricao": "Bônus +2 em Reação em corte real/alta sociedade. Exige manutenção."
        },
        {
            "nome": "Roupas de Clima Frio Extremo",
            "categoria": "Vestuário",
            "preco": 150,
            "peso": 8.0,
            "descricao": "Reduz penalidades por frio intenso em -3. Volume considerável."
        },
        {
            "nome": "Uniforme Militar Padronizado",
            "categoria": "Vestuário",
            "preco": 120,
            "peso": 5.0,
            "descricao": "Inclui botas, capa e distintivos. +1 em Reação com aliados da mesma facção."
        },

        # Acessórios e Miscelânea
        {
            "nome": "Amuleto de Proteção",
            "categoria": "Acessórios",
            "preco": 500,
            "peso": 0.2,
            "descricao": "+1 em testes de Vontade contra medo. Requer recarga mensal."
        },
        {
            "nome": "Bracelete de Foco",
            "categoria": "Acessórios",
            "preco": 380,
            "peso": 0.1,
            "descricao": "+1 em Magia ritual; +1 Esquiva ao canalizar energia luminosa."
        },
        {
            "nome": "Aljava de Flechas",
            "categoria": "Acessórios",
            "preco": 60,
            "peso": 1.0,
            "descricao": "Capacidade para 20 flechas. Inclui correias ajustáveis."
        },
        {
            "nome": "Mochila de Aventureiro",
            "categoria": "Acessórios",
            "preco": 60,
            "peso": 3.0,
            "descricao": "Capacidade 40 lb. Compartimentos para ferramentas e rações."
        },
        {
            "nome": "Cinturão de Utilidades",
            "categoria": "Acessórios",
            "preco": 50,
            "peso": 1.0,
            "descricao": "Espaço para 10 pequenos itens (facas, poções, ferramentas)."
        },
        {
            "nome": "Bússola do Dragão",
            "categoria": "Acessórios Mágicos",
            "preco": 500,
            "peso": 0.5,
            "descricao": "Artefato de rastreamento dracônico. +1 Percepção para localizar dragões."
        },
        {
            "nome": "Três Dados de Seis Faces",
            "categoria": "Acessórios Mágicos",
            "preco": 15,
            "peso": 0.1,
            "descricao": "Permite rerrolar uma falha simples por sessão (Sorte menor)."
        },

        # Ferramentas e Kits
        {
            "nome": "Kit de Primeiros Socorros",
            "categoria": "Ferramentas e Kits",
            "preco": 50,
            "peso": 2.0,
            "descricao": "+1 em Primeiros Socorros (8 usos). Requer reabastecimento."
        },
        {
            "nome": "Ferramentas de Arrombamento",
            "categoria": "Ferramentas e Kits",
            "preco": 200,
            "peso": 2.0,
            "descricao": "Inclui gazuas, serras e óleo. +2 em Arrombamento com tempo adequado."
        },
        {
            "nome": "Kit de Alquimia Portátil",
            "categoria": "Ferramentas e Kits",
            "preco": 500,
            "peso": 10.0,
            "descricao": "Permite testes de Alquimia fora do laboratório com -2 na dificuldade."
        },
        {
            "nome": "Ferramentas de Ferraria Portátil",
            "categoria": "Ferramentas e Kits",
            "preco": 800,
            "peso": 25.0,
            "descricao": "Conjunto com bigorna desmontável. Necessita fonte de calor dedicada."
        },

        # Consumíveis
        {
            "nome": "Poção de Cura Leve",
            "categoria": "Consumíveis",
            "preco": 120,
            "peso": 0.2,
            "descricao": "Recupera 1d6+1 PV imediatamente. Uso único."
        },
        {
            "nome": "Poção de Energia",
            "categoria": "Consumíveis",
            "preco": 90,
            "peso": 0.2,
            "descricao": "Recupera 1d6 PF após 10 segundos. Uso único."
        },
        {
            "nome": "Antídoto Universal",
            "categoria": "Consumíveis",
            "preco": 150,
            "peso": 0.3,
            "descricao": "+4 em testes de HT contra venenos ingeridos nas próximas 6 horas."
        },
        {
            "nome": "Ração de Viagem (1 semana)",
            "categoria": "Consumíveis",
            "preco": 50,
            "peso": 10.0,
            "descricao": "Suprimentos para uma pessoa por 7 dias. Inclui água purificada."
        },
        {
            "nome": "Flechas (pacote 12)",
            "categoria": "Consumíveis",
            "preco": 24,
            "peso": 2.0,
            "descricao": "Munição padrão para arcos. Cada flecha pesa 0,17 lb."
        },

        # Focos Mágicos
        {
            "nome": "Cajado de Aprendiz",
            "categoria": "Focos Mágicos",
            "preco": 150,
            "peso": 2.0,
            "descricao": "+1 em Magias básicas. Permite aparar com +0."
        },
        {
            "nome": "Cajado do Arquimago",
            "categoria": "Focos Mágicos",
            "preco": 900,
            "peso": 3.0,
            "descricao": "+2 em Magia e +1 Aparar contra projéteis mágicos."
        },
        {
            "nome": "Orbe Arcano de Cristal",
            "categoria": "Focos Mágicos",
            "preco": 600,
            "peso": 2.0,
            "descricao": "Canaliza energia arcana. +1 IQ em rolagens de Magia à distância."
        },
        {
            "nome": "Grimório Avançado",
            "categoria": "Focos Mágicos",
            "preco": 300,
            "peso": 5.0,
            "descricao": "+1 em Magias estudadas neste livro. Referência de rituais raros."
        },

        # Montarias e Veículos
        {
            "nome": "Cavalo de Sela",
            "categoria": "Montarias e Veículos",
            "preco": 1200,
            "peso": 100.0,
            "descricao": "Movimento Básico 8. Capacidade de carga 250 lb. Exige cuidado diário."
        },
        {
            "nome": "Cavalo de Guerra Pesado",
            "categoria": "Montarias e Veículos",
            "preco": 4000,
            "peso": 150.0,
            "descricao": "Movimento Básico 7. RD 2 natural. Treinado para combate."
        },
        {
            "nome": "Carroça Leve",
            "categoria": "Montarias e Veículos",
            "preco": 300,
            "peso": 150.0,
            "descricao": "Capacidade de carga 1000 lb. Requer 1-2 animais de tração."
        },
        {
            "nome": "Carruagem Blindada",
            "categoria": "Montarias e Veículos",
            "preco": 8000,
            "peso": 500.0,
            "descricao": "RD 4 nas laterais. Espaço para 4 passageiros e 2 guardas."
        },

        # Equipamentos de Exploração
        {
            "nome": "Tenda para 4 Pessoas",
            "categoria": "Exploração",
            "preco": 200,
            "peso": 20.0,
            "descricao": "Montagem em 10 minutos. Proteção contra chuva e vento moderado."
        },
        {
            "nome": "Corda de Seda 30m",
            "categoria": "Exploração",
            "preco": 40,
            "peso": 6.0,
            "descricao": "Suporta até 300 lb. Reduz penalidades de Escalada em -1."
        },
        {
            "nome": "Tochas (pacote 6)",
            "categoria": "Exploração",
            "preco": 10,
            "peso": 3.0,
            "descricao": "Cada tocha dura 1 hora. Iluminação equivalente a lanterna aberta."
        },
        {
            "nome": "Kit de Escalada",
            "categoria": "Exploração",
            "preco": 200,
            "peso": 20.0,
            "descricao": "Inclui pitões, martelo e grampos. +1 em Escalada em superfícies rochosas."
        },
        {
            "nome": "Lanterna a Óleo",
            "categoria": "Exploração",
            "preco": 20,
            "peso": 2.0,
            "descricao": "Consumo de 0,25 litros de óleo por hora. Iluminação concentrada."
        },
    ]

    criados = 0
    for item in itens_catalogo:
        item['tipo_item'] = classificar_tipo_item(item.get('categoria'), item.get('nome'))
        ItemCatalogo.criar_se_nao_existir(
            nome=item["nome"],
            categoria=item["categoria"],
            preco=item["preco"],
            peso=item["peso"],
            descricao=item["descricao"],
            tipo_item=item['tipo_item'],
            dano_bal_mod=item.get("dano_bal_mod"),
            dano_bal_tipo=item.get("dano_bal_tipo"),
            dano_gdp_mod=item.get("dano_gdp_mod"),
            dano_gdp_tipo=item.get("dano_gdp_tipo")
        )
        criados += 1
        print(f"✓ Item catalogado: {item['nome']} ({item['categoria']}) - {item['tipo_item']}")

    print(f"\n✅ Catálogo de itens disponível: {criados} entradas")


def popular_catalogo_vd():
    """Popula o catálogo com as principais vantagens e desvantagens do GURPS"""
    
    print("=" * 60)
    print("📚 POPULANDO CATÁLOGO DE VANTAGENS E DESVANTAGENS")
    print("=" * 60)
    
    # ==========================================
    # VANTAGENS COMUNS (GURPS 4ª Edição)
    # ==========================================
    
    vantagens = [
        # Vantagens Físicas
        ('PV Extra', 'Vantagem', 2, '2 pontos/nível', 'Aumenta Pontos de Vida em +1 por nível', 'Física'),
        ('PF Extra', 'Vantagem', 2, '2 pontos/nível', 'Aumenta Pontos de Fadiga em +1 por nível', 'Física'),
        ('Velocidade Extra', 'Vantagem', 5, '5 pontos/nível', 'Aumenta Velocidade Básica em +0,25 por nível', 'Física'),
        ('Resistência', 'Vantagem', 3, '3 pontos/nível', 'Aumenta resistência a doenças e venenos', 'Física'),
        ('Regeneração', 'Vantagem', 10, '10-100 pontos', 'Recupera PV mais rapidamente', 'Física'),
        ('Sentidos Aguçados', 'Vantagem', 2, '2 pontos/nível', 'Aumenta Percepção em +1 por nível', 'Física'),
        ('Visão Noturna', 'Vantagem', 1, '1 ponto', 'Vê no escuro', 'Física'),
        ('Visão Perfeita', 'Vantagem', 2, '2 pontos', 'Não precisa de óculos', 'Física'),
        ('Audição Aguçada', 'Vantagem', 2, '2 pontos/nível', '+1 Percepção auditiva por nível', 'Física'),
        ('Olfato Aguçado', 'Vantagem', 2, '2 pontos/nível', '+1 Percepção olfativa por nível', 'Física'),
        ('Paladar Aguçado', 'Vantagem', 2, '2 pontos/nível', '+1 Percepção gustativa por nível', 'Física'),
        ('Tato Aguçado', 'Vantagem', 2, '2 pontos/nível', '+1 Percepção tátil por nível', 'Física'),
        
        # Vantagens Mentais
        ('Vontade Extra', 'Vantagem', 5, '5 pontos/nível', 'Aumenta Vontade em +1 por nível', 'Mental'),
        ('Memória Absoluta', 'Vantagem', 10, '10 pontos', 'Nunca esquece nada', 'Mental'),
        ('Versatilidade', 'Vantagem', 5, '5 pontos', 'Reduz penalidade por default de perícia', 'Mental'),
        ('Vontade Férrea', 'Vantagem', 5, '5 pontos/nível', 'Aumenta Vontade em +1 por nível', 'Mental'),
        
        # Vantagens Sociais
        ('Status', 'Vantagem', 5, '5 pontos/nível', 'Posição social elevada', 'Social'),
        ('Reputação', 'Vantagem', 5, '5 pontos/nível', 'Boa reputação em um grupo', 'Social'),
        ('Contatos', 'Vantagem', 1, '1-20 pontos', 'Contatos úteis', 'Social'),
        ('Patrão', 'Vantagem', 5, '5-30 pontos', 'Patrão poderoso que ajuda', 'Social'),
        ('Riqueza', 'Vantagem', 10, '10-30 pontos', 'Rico ou muito rico', 'Social'),
        ('Charisma', 'Vantagem', 5, '5 pontos/nível', 'Bônus em Reações sociais', 'Social'),
        ('Aparência', 'Vantagem', 4, '4-16 pontos', 'Aparência atrativa', 'Social'),
        
        # Vantagens de Combate
        ('Reflexos em Combate', 'Vantagem', 15, '15 pontos', '+1 em percepção e ( consequentemente +1 em todas as defesas)', 'Combate'),
        ('Aparar Ampliado', 'Vantagem', 10, '10 pontos', '+1 em Aparar', 'Combate'),
        ('Bloqueio Ampliado', 'Vantagem', 5, '5 pontos', '+1 em Aparar', 'Combate'),
        ('Esquiva Ampliada', 'Vantagem', 15, '15 pontos', '+1 em Esquiva', 'Combate'),
        ('Múltiplas Defesas', 'Vantagem', 15, '15 pontos', 'Pode usar múltiplas defesas', 'Combate'),
        ('Aparar', 'Vantagem', 10, '10 pontos', 'Pode aparar com armas', 'Combate'),
        ('Armadura', 'Vantagem', 5, '5 pontos/nível', 'Armadura natural', 'Combate'),
        ('Resistência a Dano', 'Vantagem', 5, '5 pontos/nível', 'Reduz dano recebido', 'Combate'),
        
        # Vantagens Exóticas/Mágicas
        ('Aptidão Mágica', 'Vantagem', 5, '5 pontos/nível', 'Aptidão para magia', 'Mágica'),
        ('Poderes Paranormais', 'Vantagem', 5, '5-100 pontos', 'Poderes psíquicos', 'Mágica'),
        ('Voo', 'Vantagem', 40, '40 pontos', 'Pode voar', 'Mágica'),
        ('Telepatia', 'Vantagem', 20, '20 pontos', 'Lê mentes', 'Mágica'),
        ('Telecinese', 'Vantagem', 5, '5 pontos/nível', 'Move objetos com a mente', 'Mágica'),
        
        # Vantagens Especiais
        ('Sorte', 'Vantagem', 15, '15-60 pontos', 'Pode rerolar dados', 'Especial'),
        ('Sorte Extraordinária', 'Vantagem', 30, '30 pontos', 'Sorte melhorada', 'Especial'),
        ('Senso de Perigo', 'Vantagem', 30, '30 pontos', 'Avisa de perigos', 'Especial'),
        ('Pressentimento', 'Vantagem', 10, '10 pontos', 'Sente quando algo vai dar errado', 'Especial'),
    ]
    
    # ==========================================
    # DESVANTAGENS COMUNS (GURPS 4ª Edição)
    # ==========================================
    
    desvantagens = [
        # Desvantagens Físicas
        ('Baixo PA', 'Desvantagem', -10, '-10 pontos', 'Reduz Pontos de Vida em -1', 'Física'),
        ('Baixo PF', 'Desvantagem', -3, '-3 pontos/nível', 'Reduz Pontos de Fadiga em -1 por nível', 'Física'),
        ('Velocidade Reduzida', 'Desvantagem', -5, '-5 pontos/nível', 'Reduz Velocidade Básica em -0,25 por nível', 'Física'),
        ('Doença', 'Desvantagem', -5, '-5 a -30 pontos', 'Doença crônica', 'Física'),
        ('Deficiência Física', 'Desvantagem', -15, '-15 pontos', 'Perda de membro ou função', 'Física'),
        ('Cegueira', 'Desvantagem', -50, '-50 pontos', 'Totalmente cego', 'Física'),
        ('Surdez', 'Desvantagem', -20, '-20 pontos', 'Totalmente surdo', 'Física'),
        ('Mudo', 'Desvantagem', -25, '-25 pontos', 'Não pode falar', 'Física'),
        ('Coxo', 'Desvantagem', -15, '-15 pontos', 'Movimento reduzido', 'Física'),
        ('Miopia', 'Desvantagem', -25, '-25 pontos', 'Visão ruim sem óculos', 'Física'),
        ('Surdez Parcial', 'Desvantagem', -10, '-10 pontos', 'Dificuldade auditiva', 'Física'),
        ('Cegueira de Cores', 'Desvantagem', -10, '-10 pontos', 'Não distingue cores', 'Física'),
        ('Envelhecimento', 'Desvantagem', -2, '-2 pontos/nível', 'Envelhece mais rápido', 'Física'),
        
        # Desvantagens Mentais
        ('Baixa Vontade', 'Desvantagem', -5, '-5 pontos/nível', 'Reduz Vontade em -1 por nível', 'Mental'),
        ('Amnésia', 'Desvantagem', -10, '-10 pontos', 'Não lembra do passado', 'Mental'),
        ('Confusão', 'Desvantagem', -10, '-10 pontos', 'Fica confuso facilmente', 'Mental'),
        ('Delírios', 'Desvantagem', -5, '-5 a -15 pontos', 'Acredita em coisas falsas', 'Mental'),
        ('Déficit de Atenção', 'Desvantagem', -15, '-15 pontos', 'Dificuldade de concentração', 'Mental'),
        ('Fobia', 'Desvantagem', -5, '-5 a -30 pontos', 'Medo irracional', 'Mental'),
        ('Insônia', 'Desvantagem', -10, '-10 ou -15 pontos', 'Dificuldade para dormir', 'Mental'),
        ('Mania', 'Desvantagem', -5, '-5 pontos', 'Comportamento obsessivo', 'Mental'),
        ('Preguiça', 'Desvantagem', -10, '-10 pontos', 'Evita trabalho', 'Mental'),
        ('Sonolência', 'Desvantagem', -8, '-8 pontos', 'Sono excessivo', 'Mental'),
        ('Estupidez', 'Desvantagem', -10, '-10 pontos', 'Reduz IQ em -1', 'Mental'),
        
        # Desvantagens Sociais
        ('Status Baixo', 'Desvantagem', -5, '-5 pontos/nível', 'Posição social baixa', 'Social'),
        ('Reputação Negativa', 'Desvantagem', -5, '-5 pontos/nível', 'Má reputação', 'Social'),
        ('Inimigos', 'Desvantagem', -5, '-5 a -20 pontos', 'Inimigos que perseguem', 'Social'),
        ('Pobreza', 'Desvantagem', -15, '-15 ou -25 pontos', 'Pobre ou muito pobre', 'Social'),
        ('Dependência', 'Desvantagem', -5, '-5 pontos', 'Depende de alguém', 'Social'),
        ('Aparência Feia', 'Desvantagem', -4, '-4 a -16 pontos', 'Aparência desagradável', 'Social'),
        ('Odioso', 'Desvantagem', -10, '-10 pontos', 'As pessoas não gostam', 'Social'),
        ('Sociedade Secreta', 'Desvantagem', -5, '-5 a -15 pontos', 'Membro de grupo secreto', 'Social'),
        ('Código de Honra', 'Desvantagem', -5, '-5 a -15 pontos', 'Código restritivo', 'Social'),
        
        # Desvantagens de Combate
        ('Sem Aparar', 'Desvantagem', -5, '-5 pontos', 'Não pode aparar', 'Combate'),
        ('Sem Esquiva', 'Desvantagem', -15, '-15 pontos', 'Não pode esquivar', 'Combate'),
        ('Sem Bloqueio', 'Desvantagem', -5, '-5 pontos', 'Não pode bloquear', 'Combate'),
        ('Péssima Coordenação', 'Desvantagem', -5, '-5 pontos', 'Penalidade em ações coordenadas', 'Combate'),
        
        # Desvantagens Exóticas
        ('Maldição', 'Desvantagem', -5, '-5 a -75 pontos', 'Maldição sobrenatural', 'Mágica'),
        ('Vulnerabilidade', 'Desvantagem', -5, '-5 a -40 pontos', 'Vulnerável a algo específico', 'Mágica'),
        ('Dependência', 'Desvantagem', -5, '-5 a -40 pontos', 'Depende de algo', 'Mágica'),
        ('Sem Maná', 'Desvantagem', -5, '-5 pontos', 'Não pode usar magia', 'Mágica'),
        
        # Desvantagens Especiais
        ('Azar', 'Desvantagem', -15, '-15 pontos', 'Dados ruins frequentemente', 'Especial'),
        ('Destino Ruim', 'Desvantagem', -15, '-15 pontos', 'Destino desfavorável', 'Especial'),
        ('Senso de Perigo Falso', 'Desvantagem', -10, '-10 pontos', 'Avisos falsos de perigo', 'Especial'),
        ('Cilada', 'Desvantagem', -10, '-10 pontos', 'Fica preso facilmente', 'Especial'),
        
        # Desvantagens de Personalidade
        ('Excesso de Confiança', 'Desvantagem', -5, '-5 a -15 pontos', 'Subestima perigos', 'Personalidade'),
        ('Impulsividade', 'Desvantagem', -10, '-10 pontos', 'Age sem pensar', 'Personalidade'),
        ('Crueldade', 'Desvantagem', -15, '-15 pontos', 'Gosta de causar sofrimento', 'Personalidade'),
        ('Ganância', 'Desvantagem', -15, '-15 pontos', 'Obsessão por riqueza', 'Personalidade'),
        ('Gula', 'Desvantagem', -7, '-7 pontos', 'Come demais', 'Personalidade'),
        ('Lascívia', 'Desvantagem', -15, '-15 pontos', 'Obsessão sexual', 'Personalidade'),
        ('Temeridade', 'Desvantagem', -10, '-10 pontos', 'Não tem medo', 'Personalidade'),
        ('Vingativo', 'Desvantagem', -10, '-10 pontos', 'Busca vingança', 'Personalidade'),
    ]
    
    # Adiciona todas as vantagens
    for nome, tipo, custo, custo_texto, descricao, categoria in vantagens:
        VantagemDesvantagemCatalogo.criar_se_nao_existir(
            nome=nome,
            tipo=tipo,
            custo_base=custo,
            custo_texto=custo_texto,
            descricao=descricao,
            categoria=categoria
        )
        print(f"✓ {tipo}: {nome} ({custo} pts)")
    
    # Adiciona todas as desvantagens
    for nome, tipo, custo, custo_texto, descricao, categoria in desvantagens:
        VantagemDesvantagemCatalogo.criar_se_nao_existir(
            nome=nome,
            tipo=tipo,
            custo_base=custo,
            custo_texto=custo_texto,
            descricao=descricao,
            categoria=categoria
        )
        print(f"✓ {tipo}: {nome} ({custo} pts)")
    
    print(f"\n✅ Catálogo populado com {len(vantagens)} vantagens e {len(desvantagens)} desvantagens!")
    print(f"Total: {len(vantagens) + len(desvantagens)} itens")

def criar_usuarios_exemplo():
    """Cria usuários de exemplo (admin e player)"""
    print("\n" + "=" * 60)
    print("👥 CRIANDO USUÁRIOS DE EXEMPLO")
    print("=" * 60)
    
    # Admin
    admin = Usuario.buscar_por_username('admin')
    if not admin:
        print("Criando usuário admin...")
        Usuario.criar({
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'admin',
            'nome_completo': 'Administrador',
            'role': 'admin'
        })
        print("✅ Usuário admin criado (username: admin, password: admin)")
    else:
        print("ℹ️  Usuário admin já existe")
    
    # Jogador padrão
    player = Usuario.buscar_por_username('player')
    if not player:
        print("Criando usuário player...")
        Usuario.criar({
            'username': 'player',
            'email': 'player@example.com',
            'password': 'player',
            'nome_completo': 'Jogador Padrão',
            'role': 'usuario'
        })
        print("✅ Usuário player criado (username: player, password: player)")
    else:
        print("ℹ️  Usuário player já existe")

# ==========================================
# DADOS DO MUNDO SAGAS (EMBUTIDOS)
# ==========================================
_DADOS_MUNDO_SAGAS_B64 = """
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
""".strip()

DADOS_MUNDO_SAGAS = json.loads(
    zlib.decompress(base64.b64decode(_DADOS_MUNDO_SAGAS_B64)).decode('utf-8')
)

def main():
    """
    Função principal - permite escolher o que popular
    
    Uso:
        python populate_world_data.py                    # Apenas catálogo (padrão)
        python populate_world_data.py --all              # Tudo (catálogo + usuários)
        python populate_world_data.py --catalogo         # Apenas catálogo
        python populate_world_data.py --usuarios         # Apenas usuários
        python populate_world_data.py --mundo            # Apenas dados do mundo
        
    Ou configure as opções abaixo no código:
    """
    import sys
    
    # Opções de preenchimento (padrão)
    popular_catalogo = True  # Popular catálogo de vantagens/desvantagens
    popular_usuarios = False  # Criar usuários de exemplo
    popular_dados_mundo = True  # Preencher dados do mundo Sagas (alterado para True)
    
    # Processa argumentos da linha de comando
    if len(sys.argv) > 1:
        # Reset padrão se argumentos específicos forem passados
        if any(arg in sys.argv for arg in ['--catalogo', '--usuarios', '--mundo']):
            popular_catalogo = False
            popular_usuarios = False
            popular_dados_mundo = False
        
        # Define o que popular baseado nos argumentos
        if '--all' in sys.argv:
            popular_catalogo = True
            popular_usuarios = True
            popular_dados_mundo = True
        else:
            if '--catalogo' in sys.argv:
                popular_catalogo = True
            if '--usuarios' in sys.argv:
                popular_usuarios = True
            if '--mundo' in sys.argv:
                popular_dados_mundo = True
        
        # Mostra ajuda
        if '--help' in sys.argv or '-h' in sys.argv:
            print("=" * 60)
            print("🎲 SCRIPT DE PREENCHIMENTO DO MUNDO GURPS")
            print("=" * 60)
            print("\nUso:")
            print("  python populate_world_data.py [opções]")
            print("\nOpções:")
            print("  --catalogo    Popular catálogos (perícias, vantagens/desvantagens)")
            print("  --usuarios    Criar usuários de exemplo (admin, player)")
            print("  --mundo       Preencher dados do mundo (requer configuração)")
            print("  --all         Executar todas as opções")
            print("  --help, -h    Mostrar esta ajuda")
            print("\nExemplos:")
            print("  python populate_world_data.py              # Apenas catálogo (padrão)")
            print("  python populate_world_data.py --all        # Tudo")
            print("  python populate_world_data.py --usuarios   # Apenas usuários")
            return
    
    print("=" * 60)
    print("🎲 SCRIPT DE PREENCHIMENTO DO MUNDO GURPS")
    print("=" * 60)
    print(f"\nOpções selecionadas:")
    print(f"  - Popular catálogos (perícias, V/D): {popular_catalogo}")
    print(f"  - Criar usuários de exemplo: {popular_usuarios}")
    print(f"  - Preencher dados do mundo Sagas: {popular_dados_mundo}")
    print()
    
    try:
        # 1. Popular catálogos base
        if popular_catalogo:
            popular_catalogo_pericias()
            popular_catalogo_itens()
            popular_catalogo_vd()
        
        # 2. Criar usuários de exemplo
        if popular_usuarios:
            criar_usuarios_exemplo()
        
        # 3. Preencher dados do mundo (se definido)
        if popular_dados_mundo:
            if DADOS_MUNDO_SAGAS['locais'] or DADOS_MUNDO_SAGAS['personagens'] or DADOS_MUNDO_SAGAS['npcs']:
                processar_dados_mundo(DADOS_MUNDO_SAGAS)
            else:
                print("\n⚠️  Nenhum dado do mundo definido.")
        
        print("\n" + "=" * 60)
        print("✅ PREENCHIMENTO CONCLUÍDO!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erro durante preenchimento: {e}")
        print("\nCertifique-se de que:")
        print(f"  1. O banco de dados '{Config.MYSQL_DB}' existe e está acessível")
        print(f"  2. As credenciais em config.py estão corretas (Host: {Config.MYSQL_HOST})")
        print("  3. As tabelas foram criadas (execute database/schema.sql)")
        print("  4. O servidor MySQL está rodando e acessível")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

