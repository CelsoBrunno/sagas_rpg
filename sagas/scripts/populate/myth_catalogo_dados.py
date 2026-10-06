# ==========================================
# Perícias e itens próprios de Myth para os catálogos GURPS
# Os catálogos são globais (valem para todas as campanhas).
# ==========================================

_CUSTOS = {'F': '1', 'M': '3', 'D': '7', 'MD': '15'}


def _pericia(nome, atributo, dificuldade, descricao):
    return {
        'nome': nome,
        'atributo_base': atributo,
        'dificuldade': dificuldade,
        'custo_texto': _CUSTOS[dificuldade],
        'descricao': descricao,
    }


PERICIAS = [
    _pericia('Espada Larga', 'DX', 'M', 'Espadas de uma mão como a espada longa dos guerreiros das Cidades Livres.'),
    _pericia('Espada de Duas Mãos', 'DX', 'M', 'Claymores e montantes. A arma dos berserkers do Norte.'),
    _pericia('Machado/Maça', 'DX', 'M', 'Machados e maças de uma mão.'),
    _pericia('Machado/Maça de Duas Mãos', 'DX', 'M', 'Machados de batalha e martelos de guerra usados com as duas mãos.'),
    _pericia('Faca', 'DX', 'F', 'Facas e adagas. O último recurso do arqueiro quando o inimigo chega perto.'),
    _pericia('Explosivos', 'IQ', 'M', 'Preparar frascos de fogo, cargas de pólvora e pavios. Falhas críticas costumam ferir quem usa.'),
    _pericia('Ocultismo', 'IQ', 'M', 'Lendas e sinais do Escuro: mortos-vivos, maldições e o que se conta sobre os Senhores Caídos.'),
    _pericia('Armeiro', 'IQ', 'M', 'Manter e consertar armas e armaduras em campanha.'),
    _pericia('Conhecimento do Terreno', 'IQ', 'F', 'Conhecer estradas, vaus, vilas e atalhos de uma região.'),
    _pericia('Observação', 'IQ', 'M', 'Vigiar um lugar por muito tempo sem perder detalhes. Usa a Percepção.'),
]

ITENS = [
    {
        'nome': 'Claymore',
        'categoria': 'Armas Corpo-a-Corpo',
        'preco': 900,
        'peso': 3.5,
        'descricao': 'Espada de duas mãos dos berserkers do Norte. Dano: GdB+3 corte / GdP+2 perfurante. Perícia: Espada de Duas Mãos.',
        'tipo_item': 'equipamento',
        'dano_bal_mod': 3,
        'dano_bal_tipo': 'corte',
        'dano_gdp_mod': 2,
        'dano_gdp_tipo': 'perfurante',
    },
    {
        'nome': 'Faca de Arqueiro',
        'categoria': 'Armas Corpo-a-Corpo',
        'preco': 40,
        'peso': 0.5,
        'descricao': 'Faca longa carregada pelos arqueiros. Dano: GdB-2 corte / GdP perfurante. Perícia: Faca.',
        'tipo_item': 'equipamento',
        'dano_bal_mod': -2,
        'dano_bal_tipo': 'corte',
        'dano_gdp_mod': 0,
        'dano_gdp_tipo': 'perfurante',
    },
    {
        'nome': 'Flechas Incendiárias (pacote 6)',
        'categoria': 'Consumíveis',
        'preco': 60,
        'peso': 0.5,
        'descricao': 'Flechas com pano embebido em óleo. +1d-1 de queimadura e podem incendiar palha, madeira seca e mortos-vivos encharcados de óleo.',
        'tipo_item': 'consumivel',
    },
    {
        'nome': 'Frasco de Fogo Anão',
        'categoria': 'Consumíveis',
        'preco': 50,
        'peso': 0.5,
        'descricao': 'Granada anã de barro com pólvora e óleo. Arremesso: 3d explosivo em raio de 2 m. Em falha crítica explode na mão. Perícia: Arremesso (preparo: Explosivos).',
        'tipo_item': 'consumivel',
    },
    {
        'nome': 'Carga de Pólvora',
        'categoria': 'Consumíveis',
        'preco': 150,
        'peso': 2.0,
        'descricao': 'Saco de pólvora com pavio, usado pelos anões para derrubar pontes, portões e fileiras inteiras. 6d explosivo. Exige Explosivos para armar.',
        'tipo_item': 'consumivel',
    },
    {
        'nome': 'Raiz de Mandrágora',
        'categoria': 'Consumíveis',
        'preco': 100,
        'peso': 0.1,
        'descricao': 'Raiz rara carregada pelos Jornadeiros. Nas mãos de um Jornadeiro cura 1d PV. Usada contra um morto-vivo próximo, causa 2d de dano. Cada raiz serve uma vez.',
        'tipo_item': 'consumivel',
    },
    {
        'nome': 'Bolsa de Ervas do Jornadeiro',
        'categoria': 'Ferramentas e Kits',
        'preco': 80,
        'peso': 1.0,
        'descricao': 'Ataduras, ervas secas e unguentos. +1 em Primeiros Socorros e Herbologia.',
        'tipo_item': 'equipamento',
    },
]
