# ==========================================
# Criação de fichas completas de NPC (usado pelos scripts de populate)
# ==========================================

from database import Database
from models import Personagem, Atributos, VantagemDesvantagem, Pericia, Inventario

EQUIPAMENTO_CATEGORIAS = {
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

CONSUMIVEL_CATEGORIAS = {
    'consumíveis',
    'consumiveis'
}

def _normalizar_texto(valor):
    return (valor or '').strip().lower()

def classificar_tipo_item(categoria, nome):
    cat = _normalizar_texto(categoria)
    if cat in CONSUMIVEL_CATEGORIAS:
        return 'consumivel'
    if cat in EQUIPAMENTO_CATEGORIAS:
        return 'equipamento'

    nome_norm = _normalizar_texto(nome)
    if any(substr in nome_norm for substr in ['poção', 'pocao', 'antídoto', 'antidoto', 'ração', 'racao', 'flecha', 'munição', 'municao']):
        return 'consumivel'
    if any(substr in nome_norm for substr in ['armadura', 'armas', 'escudo', 'espada', 'lança', 'lanca', 'adaga', 'machado', 'martelo', 'besta', 'arco', 'foco', 'grimório', 'grimorio', 'bracelete', 'amuleto', 'cajado', 'kit', 'ferramenta', 'mochila', 'cinturão', 'cinturao', 'aljava', 'vestes']):
        return 'equipamento'
    return 'outro'

def criar_personagem_completo(dados_personagem):
    """
    Cria um personagem completo com atributos, vantagens, perícias e inventário
    
    Estrutura esperada de dados_personagem:
    {
        'nome': str,
        'raca': str,
        'categoria': str,  # 'Humano', 'Animal', 'Criatura', etc.
        'pontos_base': int,
        'biografia': str,
        'id_campanha': int (opcional),
        'atributos': {
            'ST': int,
            'DX': int,
            'IQ': int,
            'HT': int,
            'PV_extra': int (opcional),
            'PF_extra': int (opcional),
            'percepcao_extra': int (opcional),
            'vontade_extra': int (opcional)
        },
        'vantagens': [  # Lista opcional
            {'nome': str, 'custo': int, 'notas': str (opcional)}
        ],
        'desvantagens': [  # Lista opcional
            {'nome': str, 'custo': int (negativo), 'notas': str (opcional)}
        ],
        'pericias': [  # Lista opcional
            {'nome': str, 'atributo_base': 'ST'|'DX'|'IQ'|'HT', 'dificuldade': 'F'|'M'|'D'|'VD', 'pontos': int}
        ],
        'inventario': [  # Lista opcional
            {'nome': str, 'quantidade': int, 'peso': float, 'notas': str (opcional)}
        ]
    }
    """
    try:
        # Cria o personagem
        dados_personagem_db = {
            'nome': dados_personagem['nome'],
            'jogador_nome': None,  # NPCs não têm jogador
            'raca': dados_personagem.get('raca', 'Humano'),
            'pontos_base': dados_personagem.get('pontos_base', 0),
            'pontos_desvantagens_max': 0,
            'biografia': dados_personagem.get('biografia', ''),
            'tipo': 'NPC',
            'status': 'Ativo',
            'id_campanha': dados_personagem.get('id_campanha')
        }
        
        # Adiciona categoria se existir no schema
        if 'categoria' in dados_personagem:
            # Atualiza via query direta pois o model pode não ter esse campo ainda
            personagem_id = Personagem.criar(dados_personagem_db)
            try:
                Database.execute_query(
                    "UPDATE personagens SET categoria = %s, is_pc = FALSE, status_criacao = 'Aprovado' WHERE id = %s",
                    (dados_personagem['categoria'], personagem_id),
                    fetch=False
                )
            except:
                # Se categoria não existir, apenas marca como NPC
                Database.execute_query(
                    "UPDATE personagens SET is_pc = FALSE, status_criacao = 'Aprovado' WHERE id = %s",
                    (personagem_id,),
                    fetch=False
                )
        else:
            personagem_id = Personagem.criar(dados_personagem_db)
            Database.execute_query(
                "UPDATE personagens SET is_pc = FALSE, status_criacao = 'Aprovado' WHERE id = %s",
                (personagem_id,),
                fetch=False
            )
        
        print(f"✅ Personagem criado: {dados_personagem['nome']} (ID: {personagem_id})")
        
        # Cria atributos
        atributos = dados_personagem.get('atributos', {})
        Atributos.criar(
            personagem_id,
            ST=atributos.get('ST', 10),
            DX=atributos.get('DX', 10),
            IQ=atributos.get('IQ', 10),
            HT=atributos.get('HT', 10),
            PV_extra=atributos.get('PV_extra', 0),
            PF_extra=atributos.get('PF_extra', 0),
            percepcao_extra=atributos.get('percepcao_extra', 0),
            vontade_extra=atributos.get('vontade_extra', 0)
        )
        print(f"  └─ Atributos criados")
        
        # Adiciona vantagens
        vantagens = dados_personagem.get('vantagens', [])
        for vantagem in vantagens:
            try:
                VantagemDesvantagem.criar(
                    personagem_id,
                    vantagem['nome'],
                    vantagem['custo'],
                    vantagem.get('notas', '')
                )
            except Exception as e:
                print(f"  ⚠️  Erro ao adicionar vantagem {vantagem['nome']}: {str(e)}")
        if vantagens:
            print(f"  └─ {len(vantagens)} vantagem(ns) adicionada(s)")
        
        # Adiciona desvantagens
        desvantagens = dados_personagem.get('desvantagens', [])
        for desvantagem in desvantagens:
            try:
                VantagemDesvantagem.criar(
                    personagem_id,
                    desvantagem['nome'],
                    desvantagem['custo'],  # Já é negativo
                    desvantagem.get('notas', '')
                )
            except Exception as e:
                print(f"  ⚠️  Erro ao adicionar desvantagem {desvantagem['nome']}: {str(e)}")
        if desvantagens:
            print(f"  └─ {len(desvantagens)} desvantagem(ns) adicionada(s)")
        
        # Adiciona perícias
        pericias = dados_personagem.get('pericias', [])
        for pericia in pericias:
            try:
                Pericia.criar(
                    personagem_id,
                    pericia['nome'],
                    pericia.get('atributo_base', 'DX'),
                    pericia.get('dificuldade', 'M'),
                    pericia.get('pontos', 0)
                )
            except Exception as e:
                print(f"  ⚠️  Erro ao adicionar perícia {pericia['nome']}: {str(e)}")
        if pericias:
            print(f"  └─ {len(pericias)} perícia(s) adicionada(s)")
        
        # Adiciona inventário
        inventario = dados_personagem.get('inventario', [])
        for item in inventario:
            try:
                tipo_item = item.get('tipo_item') or classificar_tipo_item(item.get('categoria'), item.get('nome'))
                item['tipo_item'] = tipo_item
                Inventario.criar(
                    personagem_id=personagem_id,
                    nome_item=item['nome'],
                    quantidade=item.get('quantidade', 1),
                    peso=item.get('peso', 0.0),
                    notas=item.get('notas', ''),
                    tipo_item=tipo_item
                )
            except Exception as e:
                print(f"  ⚠️  Erro ao adicionar item {item['nome']}: {str(e)}")
        if inventario:
            print(f"  └─ {len(inventario)} item(ns) adicionado(s) ao inventário")
        
        # Recalcula pontos gastos
        Personagem.recalcular_pontos_gastos(personagem_id)
        
        return personagem_id
        
    except Exception as e:
        print(f"❌ Erro ao criar personagem {dados_personagem.get('nome', 'Desconhecido')}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
