# ==========================================
# Os Cinco Campeões (Myth: The Fallen Lords) - fichas GURPS 4e de ~250 pontos
# descricao_breve: o que um soldado da Legião sabe no ano 17. descricao_completa: só o mestre.
# O resgate de Alric ainda não aconteceu no início da campanha.
# ==========================================

CAMPEOES = [
    {
        'nome': "ki'Angsi",
        'status': 'Vivo',
        'local': None,
        'descricao_breve': (
            "O melhor arqueiro dos fir'Bolg, segundo os próprios fir'Bolg, e ninguém na Legião discorda. "
            'Atira mais rápido e mais longe que qualquer outro arqueiro e quase nunca erra. Fala pouco com humanos '
            'e menos ainda com anões. Contam que já derrubou um Ghôl em plena corrida a duzentos passos.'
        ),
        'descricao_completa': (
            'CINCO CAMPEÕES: mais tarde no ano 17 é escolhido para a missão que atravessa a Cloudspine de balão atrás '
            'de Alric, desaparecido a leste da Barreira.\n\n'
            'ARCO DA PETRIFICAÇÃO: durante a missão encontra um arco de gigante que dois homens juntos não conseguem '
            'dobrar. Só ele consegue armá-lo. As flechas transformam o alvo em pedra. Não está no inventário: entregue '
            'quando a história chegar lá (sugestão: 1d+2 perfurante; alvo vivo atingido faz HT-3 ou vira pedra).\n\n'
            'NA MESA: bom contato para um arqueiro fir\'Bolg do grupo. Respeita quem prova pontaria, despreza quem se gaba.'
        ),
        'ficha': {
            'raca': "Fir'Bolg",
            'pontos_base': 250,
            'atributos': {'ST': 11, 'DX': 16, 'IQ': 11, 'HT': 12, 'PF_extra': 3, 'percepcao_extra': 3},
            'vantagens': [
                {'nome': 'Reflexos em Combate', 'custo': 15},
                {'nome': 'Visão Aguçada 3', 'custo': 6},
                {'nome': 'Silencioso 2', 'custo': 10},
                {'nome': 'Reputação +2', 'custo': 5, 'notas': 'Entre os arqueiros da Legião'},
                {'nome': 'Senso de Direção', 'custo': 5},
                {'nome': 'Destemor 2', 'custo': 4},
            ],
            'desvantagens': [
                {'nome': 'Senso do Dever', 'custo': -10, 'notas': "Povo fir'Bolg"},
                {'nome': 'Solitário', 'custo': -5},
                {'nome': 'Teimosia', 'custo': -5},
                {'nome': 'Excesso de Confiança', 'custo': -5},
            ],
            'pericias': [
                {'nome': 'Arco', 'atributo_base': 'DX', 'dificuldade': 'M', 'pontos': 20},
                {'nome': 'Faca', 'atributo_base': 'DX', 'dificuldade': 'F', 'pontos': 2},
                {'nome': 'Furtividade', 'atributo_base': 'DX', 'dificuldade': 'M', 'pontos': 4},
                {'nome': 'Sobrevivência (Floresta)', 'atributo_base': 'IQ', 'dificuldade': 'M', 'pontos': 2},
                {'nome': 'Rastreamento', 'atributo_base': 'IQ', 'dificuldade': 'M', 'pontos': 2},
                {'nome': 'Observação', 'atributo_base': 'IQ', 'dificuldade': 'M', 'pontos': 2},
                {'nome': 'Camuflagem', 'atributo_base': 'IQ', 'dificuldade': 'F', 'pontos': 1},
                {'nome': 'Armeiro (Arcos)', 'atributo_base': 'IQ', 'dificuldade': 'M', 'pontos': 1},
            ],
            'inventario': [
                {'nome': 'Arco longo fir\'Bolg', 'quantidade': 1, 'peso': 1.5, 'notas': '1d+2 perfurante. Alcance 15x/20x ST',
                 'tipo_item': 'equipamento'},
                {'nome': 'Flechas Incendiárias (pacote 6)', 'quantidade': 2, 'peso': 0.5},
                {'nome': 'Flechas comuns', 'quantidade': 24, 'peso': 0.05, 'tipo_item': 'consumivel'},
                {'nome': 'Faca de Arqueiro', 'quantidade': 1, 'peso': 0.5},
            ],
        },
    },
    {
        'nome': 'Oleg',
        'status': 'Vivo',
        'local': None,
        'descricao_breve': (
            'Granadeiro anão de Myrgard, mais surdo a cada batalha e mais feliz a cada explosão. Joga frascos de fogo '
            'mais rápido e mais longe que qualquer outro anão. Os soldados dizem que, quando a mochila dele fica vazia, '
            'é hora de tapar os ouvidos.'
        ),
        'descricao_completa': (
            'CINCO CAMPEÕES: integra a missão de resgate de Alric a leste da Barreira. Na fuga, segura a retaguarda '
            'sozinho: "quando vimos que a mochila dele estava vazia, tapamos os ouvidos... pedaços de Thrall choveram por horas".\n\n'
            'NA MESA: mentor natural para um granadeiro do grupo. Odeia Ghôls com uma paixão que beira a loucura. '
            'Rival amistoso do Velho Brannoch.'
        ),
        'ficha': {
            'raca': 'Anão',
            'pontos_base': 250,
            'atributos': {'ST': 12, 'DX': 13, 'IQ': 12, 'HT': 14, 'PV_extra': 2, 'vontade_extra': 2},
            'vantagens': [
                {'nome': 'Reflexos em Combate', 'custo': 15},
                {'nome': 'Sortudo', 'custo': 15},
                {'nome': 'Destemor 2', 'custo': 4},
                {'nome': 'Duro de Matar 2', 'custo': 4},
                {'nome': 'Visão Noturna 3', 'custo': 3},
            ],
            'desvantagens': [
                {'nome': 'Hipoaudição', 'custo': -10, 'notas': 'Explosões demais'},
                {'nome': 'Intolerância', 'custo': -5, 'notas': 'Ghôls'},
                {'nome': 'Piromania', 'custo': -5},
                {'nome': 'Teimosia', 'custo': -5},
            ],
            'pericias': [
                {'nome': 'Arremesso', 'atributo_base': 'DX', 'dificuldade': 'M', 'pontos': 24},
                {'nome': 'Explosivos', 'atributo_base': 'IQ', 'dificuldade': 'M', 'pontos': 16},
                {'nome': 'Machado/Maça', 'atributo_base': 'DX', 'dificuldade': 'M', 'pontos': 8},
                {'nome': 'Escudo', 'atributo_base': 'DX', 'dificuldade': 'F', 'pontos': 2},
                {'nome': 'Armeiro', 'atributo_base': 'IQ', 'dificuldade': 'M', 'pontos': 2},
                {'nome': 'Engenharia (Combate)', 'atributo_base': 'IQ', 'dificuldade': 'D', 'pontos': 2},
                {'nome': 'Sobrevivência (Montanha)', 'atributo_base': 'IQ', 'dificuldade': 'M', 'pontos': 1},
            ],
            'inventario': [
                {'nome': 'Frasco de Fogo Anão', 'quantidade': 12, 'peso': 0.5},
                {'nome': 'Carga de Pólvora', 'quantidade': 2, 'peso': 2.0},
                {'nome': 'Machado', 'quantidade': 1, 'peso': 2.0, 'notas': 'GdB+2 corte', 'tipo_item': 'equipamento'},
                {'nome': 'Escudo pequeno', 'quantidade': 1, 'peso': 4.0, 'notas': 'BD 1', 'tipo_item': 'equipamento'},
            ],
        },
    },
    {
        'nome': 'Truan das Cem Batalhas',
        'status': 'Vivo',
        'local': None,
        'descricao_breve': (
            'Berserker do Norte, veterano de mais combates do que consegue lembrar, daí o nome. Luta sem armadura, '
            'com uma claymore enorme, e os mais novos juram que ele nunca recuou. Alric confia nele para os serviços '
            'que ninguém mais aceitaria.'
        ),
        'descricao_completa': (
            'A CABEÇA: foi Truan quem, a pedido de Alric, desceu sozinho às ruínas e trouxe a Cabeça. Não fala disso '
            'com ninguém e tem pesadelos desde então.\n\n'
            'CINCO CAMPEÕES: lidera na prática a missão que resgata Alric das mãos do Enganador, onde Balor o interroga. '
            'Na fuga, ajuda Alric a matar a sombra Sinis.\n\n'
            'NA MESA: modelo de herói para um berserker do grupo. Respeita coragem acima de tudo.'
        ),
        'ficha': {
            'raca': 'Humano',
            'pontos_base': 250,
            'atributos': {'ST': 15, 'DX': 15, 'IQ': 10, 'HT': 13, 'PV_extra': 3, 'PF_extra': 3},
            'vantagens': [
                {'nome': 'Reflexos em Combate', 'custo': 15},
                {'nome': 'Alta Tolerância à Dor', 'custo': 10},
                {'nome': 'Duro de Matar 3', 'custo': 6},
                {'nome': 'Reputação +2', 'custo': 5, 'notas': 'Na Legião: "nunca recuou"'},
            ],
            'desvantagens': [
                {'nome': 'Fúria', 'custo': -10, 'notas': 'Berserk, autocontrole 12'},
                {'nome': 'Senso do Dever', 'custo': -10, 'notas': 'Alric e a Legião'},
                {'nome': 'Pesadelos', 'custo': -5},
            ],
            'pericias': [
                {'nome': 'Espada de Duas Mãos', 'atributo_base': 'DX', 'dificuldade': 'M', 'pontos': 24},
                {'nome': 'Briga', 'atributo_base': 'DX', 'dificuldade': 'F', 'pontos': 2},
                {'nome': 'Intimidação', 'atributo_base': 'IQ', 'dificuldade': 'M', 'pontos': 4},
                {'nome': 'Tática', 'atributo_base': 'IQ', 'dificuldade': 'D', 'pontos': 4},
                {'nome': 'Liderança', 'atributo_base': 'IQ', 'dificuldade': 'M', 'pontos': 4},
                {'nome': 'Rastreamento', 'atributo_base': 'IQ', 'dificuldade': 'M', 'pontos': 2},
                {'nome': 'Sobrevivência (Montanha)', 'atributo_base': 'IQ', 'dificuldade': 'M', 'pontos': 2},
            ],
            'inventario': [
                {'nome': 'Claymore', 'quantidade': 1, 'peso': 3.5},
            ],
        },
    },
    {
        'nome': 'Turgeis do Aço Ardente',
        'status': 'Vivo',
        'local': None,
        'descricao_breve': (
            'Berserker jovem e famoso pela velocidade. Dizem que golpeia tão rápido que o inimigo morre antes de se '
            'recuperar do primeiro corte. Ri durante as batalhas, o que assusta os próprios companheiros.'
        ),
        'descricao_completa': (
            'CINCO CAMPEÕES: integra a missão de resgate de Alric.\n\n'
            'FUTURO: anos depois luta na Escadaria do Pesar contra os restos do exército de mortos-vivos do Enganador.\n\n'
            'NA MESA: rival de treino perfeito para um berserker do grupo. Impulsivo: aceita qualquer desafio.'
        ),
        'ficha': {
            'raca': 'Humano',
            'pontos_base': 250,
            'atributos': {'ST': 14, 'DX': 16, 'IQ': 10, 'HT': 12, 'PV_extra': 2, 'PF_extra': 2},
            'vantagens': [
                {'nome': 'Ataque Extra 1', 'custo': 25},
                {'nome': 'Reflexos em Combate', 'custo': 15},
                {'nome': 'Esquiva Ampliada', 'custo': 15},
            ],
            'desvantagens': [
                {'nome': 'Fúria', 'custo': -10, 'notas': 'Berserk, autocontrole 12'},
                {'nome': 'Impulsividade', 'custo': -10},
                {'nome': 'Excesso de Confiança', 'custo': -5},
            ],
            'pericias': [
                {'nome': 'Espada de Duas Mãos', 'atributo_base': 'DX', 'dificuldade': 'M', 'pontos': 20},
                {'nome': 'Briga', 'atributo_base': 'DX', 'dificuldade': 'F', 'pontos': 1},
                {'nome': 'Corrida', 'atributo_base': 'HT', 'dificuldade': 'M', 'pontos': 2},
                {'nome': 'Intimidação', 'atributo_base': 'IQ', 'dificuldade': 'M', 'pontos': 2},
                {'nome': 'Rastreamento', 'atributo_base': 'IQ', 'dificuldade': 'M', 'pontos': 2},
            ],
            'inventario': [
                {'nome': 'Claymore', 'quantidade': 1, 'peso': 3.5},
            ],
        },
    },
    {
        'nome': 'Jornadeiro sem nome',
        'status': 'Vivo',
        'local': None,
        'descricao_breve': (
            'Jornadeiro mascarado que acompanha a Legião há anos. Nunca disse o próprio nome e ninguém ousa perguntar. '
            'Os feridos que passam pelas mãos dele costumam sobreviver, e os mortos que se aproximam dele costumam cair.'
        ),
        'descricao_completa': (
            'CINCO CAMPEÕES: é o curandeiro da missão de resgate de Alric. O jogo não dá nome a ele; alguns dizem que '
            'seria Twelve Motion Jeweled Skull, mas isso não é oficial. Use como quiser.\n\n'
            'SEGREDO: como todo Jornadeiro, carrega a culpa da queda de Muirthemne e do Império Cath Bruig. '
            'Conhece lendas antigas que podem ajudar o grupo, se ganharem a confiança dele.\n\n'
            'NA MESA: mentor para um Jornadeiro do grupo, ou a ponte entre a Irmã Ysolde e os Campeões.'
        ),
        'ficha': {
            'raca': 'Humano',
            'pontos_base': 250,
            'atributos': {'ST': 10, 'DX': 12, 'IQ': 14, 'HT': 12, 'PF_extra': 4, 'vontade_extra': 4},
            'vantagens': [
                {'nome': 'Cura', 'custo': 24, 'notas': 'Só com raiz de mandrágora (-20%)'},
                {'nome': 'Senso do Perigo', 'custo': 15},
                {'nome': 'Imunidade a Doenças', 'custo': 10},
                {'nome': 'Destemor 3', 'custo': 6},
            ],
            'desvantagens': [
                {'nome': 'Voto', 'custo': -10, 'notas': 'Penitência: nunca mostrar o rosto nem dizer o nome'},
                {'nome': 'Senso do Dever', 'custo': -10, 'notas': 'Os feridos'},
                {'nome': 'Segredo', 'custo': -5, 'notas': 'O passado dos Jornadeiros'},
            ],
            'pericias': [
                {'nome': 'Primeiros Socorros', 'atributo_base': 'IQ', 'dificuldade': 'F', 'pontos': 4},
                {'nome': 'Médico', 'atributo_base': 'IQ', 'dificuldade': 'D', 'pontos': 8},
                {'nome': 'Herbalismo', 'atributo_base': 'IQ', 'dificuldade': 'D', 'pontos': 8},
                {'nome': 'Diagnóstico', 'atributo_base': 'IQ', 'dificuldade': 'D', 'pontos': 4},
                {'nome': 'Ocultismo', 'atributo_base': 'IQ', 'dificuldade': 'M', 'pontos': 8},
                {'nome': 'Exorcismo', 'atributo_base': 'IQ', 'dificuldade': 'D', 'pontos': 4},
                {'nome': 'História', 'atributo_base': 'IQ', 'dificuldade': 'D', 'pontos': 4},
                {'nome': 'Bastão', 'atributo_base': 'DX', 'dificuldade': 'M', 'pontos': 8},
                {'nome': 'Sobrevivência (Floresta)', 'atributo_base': 'IQ', 'dificuldade': 'M', 'pontos': 4},
            ],
            'inventario': [
                {'nome': 'Raiz de Mandrágora', 'quantidade': 5, 'peso': 0.1},
                {'nome': 'Bolsa de Ervas do Jornadeiro', 'quantidade': 1, 'peso': 1.0},
                {'nome': 'Bastão', 'quantidade': 1, 'peso': 2.0, 'notas': 'GdB+2 contusão', 'tipo_item': 'equipamento'},
            ],
        },
    },
]
