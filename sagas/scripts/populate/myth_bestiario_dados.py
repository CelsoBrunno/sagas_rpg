# ==========================================
# Bestiário do Escuro (Myth, ano 17) - adaptação própria para GURPS 4e
# descricao_publica: o que um soldado da Legião sabe. descricao_mestre: só o mestre.
# Todas começam bloqueadas; o mestre revela no site quando o grupo encontra a criatura.
# ==========================================

CRIATURAS = [
    {
        'nome': 'Thrall',
        'categoria': 'Morto-vivo',
        'descricao_publica': (
            'Cadáveres reanimados de soldados e camponeses mortos pelo Escuro. Lentos, silenciosos e incansáveis, '
            'avançam em fileiras com machados enferrujados. Não sentem dor nem medo. '
            'Dizem que atravessam rios andando pelo fundo.'
        ),
        'descricao_mestre': (
            'Atacam em massa. Fogo e explosivos são a melhor resposta. Não respiram: podem surgir de dentro da água '
            'em vaus e margens. Deslocamento baixo; um grupo móvel consegue fugir deles.'
        ),
        'ficha': {
            'pontos_base': 60,
            'atributos': {'ST': 12, 'DX': 10, 'IQ': 6, 'HT': 12, 'PV_extra': 4},
            'vantagens': [
                {'nome': 'Resistência a Dano', 'custo': 10, 'notas': 'RD 2 (carne morta)'},
                {'nome': 'Imunidade a Dor', 'custo': 10, 'notas': 'Não sofre choque nem atordoamento por ferimentos'},
                {'nome': 'Não Respira', 'custo': 20, 'notas': 'Anda sob a água'},
            ],
            'desvantagens': [
                {'nome': 'Velocidade Reduzida', 'custo': -10, 'notas': '-0,5 na Velocidade Básica'},
            ],
            'pericias': [
                {'nome': 'Machado/Maça', 'atributo_base': 'DX', 'dificuldade': 'M', 'pontos': 4},
            ],
            'inventario': [
                {'nome': 'Machado de Batalha', 'quantidade': 1, 'peso': 4.0, 'notas': 'Enferrujado'},
            ],
        },
    },
    {
        'nome': 'Ghôl',
        'categoria': 'Besta',
        'imagem_url': '/static/images/bestiario/ghol.jpg',
        'galeria': ['/static/images/bestiario/ghol_prologo.webp'],
        'descricao_publica': (
            'Uma raça bestial vinda das Terras Ermas. Do tamanho de cães grandes, arrastam os nós dos dedos no chão '
            'enquanto correm e carregam cutelos do tamanho do próprio braço. Também arremessam o que encontram: '
            'pedras, ossos, pedaços de cadáveres.\n\n'
            'São rapidíssimos, o que faz deles batedores incríveis. Fracos, mas capazes de subir uma encosta '
            'correndo e retalhar um grupo de arqueiros antes que eles tenham tempo de reagir. Nunca foram uma '
            'raça especialmente esperta. Sozinhos, são covardes notórios; em bando, a coragem cresce até a '
            'imprudência.\n\n'
            'São carniceiros e comem qualquer coisa orgânica, de líquens a criaturas vivas, com ossos e tudo. '
            'O bem mais precioso de um Ghôl é seu saco: ali carrega carne morta, restos de osso e metal e pequenos '
            'troféus tirados dos inimigos mortos. Acredita-se que pedaços de pele ou cabelo guardam a alma do '
            'morto e que às vezes são oferecidos aos Deuses Sombrios em cerimônias imundas.\n\n'
            'Adoram enormes pedras brutas, arrastadas há eras para os campos abaixo de suas montanhas. Dizem que '
            'só eles ainda lembram os nomes dos Deuses Sombrios.\n\n'
            'São inimigos dos anões desde o começo dos tempos. Saquear Myrgard foi o sonho raivoso deles por '
            'séculos. Na Era do Vento quase conseguiram, até que Connacht chegou a tempo e uniu os reinos anões ao '
            'Império de Cath Bruig. Nesta guerra, juraram lealdade a Balor em troca de Myrgard, e conseguiram: '
            'tomaram a cidade e expulsaram os anões. Celebram a conquista com banquetes sob a lua cheia, '
            'encenando o saque para nunca esquecer seu momento de triunfo.\n\n'
            'Dão a si mesmos nomes como Esmagador, Triturador, Rangedor, Retalhador, Estripador, Uivador, '
            'Açougueiro e Mutilador.\n\n'
            '"Os Ghôls sempre estiveram em guerra com os anões em torno de Myrgard e Stoneheim, e a violação do '
            'lar ancestral dos anões tem sido o sonho raivoso dos Ghôls há séculos."'
        ),
        'descricao_mestre': (
            'CASTAS: além do Ghôl comum, existem os Ghôl Brutos (os maiores da horda) e os Sacerdotes Ghôl, que '
            'lideram o bando e oferecem sacrifícios aos Deuses Sombrios. Podem virar entradas próprias no '
            'bestiário. Possível líder da tomada de Myrgard: Fang-Grinder.\n\n'
            'A PEDRA-DEUS: a relíquia mais sagrada da raça é a Pedra-Deus ancestral, um bloco de pedra bruta de '
            'centenas de toneladas que eles adoram desde o nascimento da raça e rolam para onde migram. Hoje está '
            'em Myrgard. Na tomada da cidade, o Nivelador ajudou os Ghôls; Stoneheim preferiu se emparedar a ter '
            'o mesmo destino.\n\n'
            'FUTURO (não revelar): trinta anos depois da vitória, o batedor anão Balin entra em Myrgard de balão '
            'com um bando de anões, destrói a Pedra-Deus e expulsa os Ghôls. Sem o ídolo, eles juram "devorar os '
            'anões até não existirem mais" e seguem Soulblighter na guerra seguinte, como serviram a Balor.\n\n'
            'TÁTICA: caçam arqueiros e jornadeiros isolados. Pouca vida: um bom golpe derruba. Uma linha fechada '
            'de escudos quebra o bando. Fogem quando a luta fica difícil e voltam na hora errada.\n\n'
            'REGRAS: sobem encostas íngremes correndo, sem penalidade de terreno. Arremessam objetos (pedras, '
            'ossos, cabeças) a até 8 m. Resistentes a paralisia: +3 no teste de HT contra o gás do Wight e '
            'duração pela metade.'
        ),
        'ficha': {
            'pontos_base': 60,
            'atributos': {'ST': 9, 'DX': 13, 'IQ': 8, 'HT': 11},
            'vantagens': [
                {'nome': 'Velocidade Extra', 'custo': 10, 'notas': '+0,5 na Velocidade Básica'},
                {'nome': 'Visão Noturna', 'custo': 1},
                {'nome': 'Olfato Aguçado', 'custo': 4, 'notas': '+2 para farejar sangue'},
            ],
            'desvantagens': [
                {'nome': 'Covardia', 'custo': -10, 'notas': 'Foge quando o bando perde metade'},
            ],
            'pericias': [
                {'nome': 'Machado/Maça', 'atributo_base': 'DX', 'dificuldade': 'M', 'pontos': 2},
                {'nome': 'Arremesso', 'atributo_base': 'DX', 'dificuldade': 'M', 'pontos': 2},
                {'nome': 'Furtividade', 'atributo_base': 'DX', 'dificuldade': 'M', 'pontos': 2},
            ],
            'inventario': [
                {'nome': 'Cutelo', 'quantidade': 1, 'peso': 1.0, 'tipo_item': 'equipamento', 'notas': 'GdB corte'},
            ],
        },
    },
    {
        'nome': 'Soulless',
        'categoria': 'Morto-vivo',
        'imagem_url': '/static/images/bestiario/soulless.jpg',
        'galeria': ['/static/images/bestiario/soulless_bando.png'],
        'descricao_publica': (
            'Almas literalmente roubadas por feitiçaria. No Oeste são chamados de Homens Ocos. São esqueletos sem '
            'cintura nem pernas, envoltos numa nuvem de vapor escuro, que flutuam devagar pelos campos e deixam '
            'peste e corrupção por onde passam. Deslizam rápido por cima de quase qualquer terreno difícil ou '
            'obstáculo que nenhuma outra criatura consegue atravessar.\n\n'
            'Levam às costas uma aljava de dardos farpados e os arremessam de longe com uma precisão assustadora. '
            'O que mais se teme neles é o veneno pegajoso com que untam os dardos antes da batalha: causa uma dor '
            'excruciante, que vai crescendo até matar, e as feridas contaminadas nunca saram.\n\n'
            'Um miasma de peste e morte sai o tempo todo de seus corpos. O fedor faz guerreiros calejados '
            'vomitarem, e as plantas que eles tocam secam até virar pó ou veneno.\n\n'
            '"Chamados de Homens Ocos no Oeste, os Soulless são mais temidos pelo veneno pegajoso com que untam '
            'seus dardos antes da batalha, pois as feridas contaminadas pela toxina nunca saram..."\n\n'
            '"...eles varreram os campos corrompendo tudo o que tocavam, e o fedor que deixavam para trás era o de '
            'um matadouro abandonado às pressas."'
        ),
        'descricao_mestre': (
            'COMO SÃO FEITOS: os Homens Ocos são cobiçados porque mantêm a inteligência. Para criar um, a mente da '
            'vítima precisa estar disposta. O criador descobre a única coisa que a pessoa um dia amou, uma memória '
            'ou uma ideia, e apaga isso da mente dela. Sem razão para viver, a alma se corrompe com facilidade. '
            '"Inteligência sem consciência." São mantidos no ar pela memória das pernas. Um Soulless pode pensar, '
            'planejar e até conversar, mas não sente nada.\n\n'
            'O VENENO: fazem os próprios dardos com galhos retorcidos e farpas de madeira, e mergulham as pontas '
            'numa gosma preta tirada de ervas que murcham sob eles.\n\n'
            'TÁTICA: flutuam, então ignoram terreno ruim, água e pântano. Frágeis em corpo a corpo e sem armadura. '
            'Arqueiros e o Fir\'Bolg são a resposta natural.\n\n'
            'REGRAS: dardos até 20 m. Veneno: quem for ferido faz HT-2; se falhar, fica com -2 por agonia e perde '
            '1 PV a cada 10 minutos até ser tratado (Primeiros Socorros com Bolsa de Ervas do Jornadeiro, ou '
            'cura de um jornadeiro). A ferida envenenada não cura naturalmente. Imunes a paralisia (gás do Wight), '
            'petrificação, gases e confusão.'
        ),
        'ficha': {
            'pontos_base': 80,
            'atributos': {'ST': 9, 'DX': 12, 'IQ': 9, 'HT': 10},
            'vantagens': [
                {'nome': 'Voo', 'custo': 40, 'notas': 'Flutuação baixa, até 2 m do chão'},
                {'nome': 'Não Respira', 'custo': 20},
                {'nome': 'Imunidade a Dor', 'custo': 10},
            ],
            'pericias': [
                {'nome': 'Arremesso', 'atributo_base': 'DX', 'dificuldade': 'M', 'pontos': 4},
            ],
            'inventario': [
                {'nome': 'Dardos (pacote 6)', 'quantidade': 1, 'peso': 3.0, 'tipo_item': 'consumivel', 'notas': 'GdP+1 perfurante'},
            ],
        },
    },
    {
        'nome': 'Wight',
        'categoria': 'Morto-vivo',
        'descricao_publica': (
            'Cadáveres inchados e cobertos de feridas que se arrastam até as linhas inimigas. Quando são feridos, '
            'explodem numa nuvem de gás que paralisa quem estiver perto. Os veteranos repetem: mate-os de longe.'
        ),
        'descricao_mestre': (
            'Ao receber dano de corte ou perfuração, ou ao morrer, explode: todos a até 2 m fazem HT-3 '
            'ou ficam paralisados por 1d minutos. Mortos-vivos não são afetados. Use para punir quem avança sem pensar.'
        ),
        'ficha': {
            'pontos_base': 40,
            'atributos': {'ST': 10, 'DX': 8, 'IQ': 6, 'HT': 8},
            'vantagens': [
                {'nome': 'Imunidade a Dor', 'custo': 10},
                {'nome': 'Explosão Paralisante', 'custo': 20, 'notas': 'HT-3 em raio de 2 m ou paralisia por 1d minutos'},
            ],
            'desvantagens': [
                {'nome': 'Velocidade Reduzida', 'custo': -10, 'notas': '-0,5 na Velocidade Básica'},
            ],
            'pericias': [
                {'nome': 'Briga', 'atributo_base': 'DX', 'dificuldade': 'F', 'pontos': 1},
            ],
        },
    },
    {
        'nome': 'Myrmidon',
        'categoria': 'Morto-vivo',
        'imagem_url': '/static/images/bestiario/myrmidon.jpg',
        'galeria': ['/static/images/bestiario/myrmidon_cabecas.jpg'],
        'descricao_publica': (
            'Uma raça de guerreiros que traiu a Luz quando Balor lhes prometeu a imortalidade. Trezentos anos '
            'depois, seus corpos apodrecidos ainda caminham, mantidos inteiros apenas por ataduras podres e pelo '
            'desejo de arrancar a carne dos vivos.\n\n'
            'Cada Myrmidon carrega duas lâminas Gridaksma: um fêmur humano com uma lâmina de foice de aço presa '
            'em cada ponta. Poucos golpes certeiros abrem caminho através de quase qualquer coisa. São rápidos '
            'e são a tropa de choque dos Senhores Caídos.\n\n'
            'Eram um povo guerreiro do Norte, dos Doze Duns. Há muito tempo encontraram um santuário antigo com '
            'pergaminhos e aprenderam ali as velhas artes da batalha. Suas técnicas rápidas e mortais os tornaram '
            'temíveis até para os Myrkridia, e foi assim que ganharam o nome Myrmidon. Abandonaram o próprio povo '
            'para seguir Balor e os Senhores Caídos, e por isso o Norte os chama de Os Sem-Parentes. '
            'Os berserkers do Norte os odeiam acima de tudo.\n\n'
            'Dão a si mesmos nomes como Fúria-Sangrenta, Fome-de-Sangue, Sede-de-Alma, Esfola-Pele, Lasca-Osso, '
            'Rasga-Carne, Carícia-da-Morte e Coração-de-Ferro.\n\n'
            '"Desejosos de poder e imortalidade, os guerreiros Myrmidons deixaram seus parentes do Norte para se '
            'juntar a Balor e aos Senhores Caídos, e assim ficaram conhecidos como Os Sem-Parentes."\n\n'
            '"Quando ainda eram carne e sangue, os Myrmidons eram muito vaidosos com seus cabelos longos e suas '
            'pinturas de guerra, e passavam a véspera da batalha diante de um espelho em vez de num saco de dormir."'
        ),
        'descricao_mestre': (
            'HISTÓRIA ANTIGA: na Era do Vento, os Doze Duns caíram diante do exército sombrio de Moagim. Ravanna, '
            'com a ajuda de Damas, liderou a fuga de milhares de refugiados e forjou a aliança entre os Duns, '
            'Gower e Llancarfan. Cuidado ao citar esses nomes perto de Shiver e Soulblighter.\n\n'
            'BERSERKERS: os berserkers são o povo que os Myrmidons abandonaram. Quando um berserker e um Myrmidon '
            'se veem, os dois lutam até a morte. Bom gancho para um PC do Norte.\n\n'
            'TÁTICA: dois ataques por turno, um com cada Gridaksma. Não usam armadura: o corpo é só carne podre e '
            'ataduras, então fogo pega bem neles. Explosivos e machados pesados também funcionam.\n\n'
            'FICHA: a ficha GURPS ainda está com Espada Larga, duas Espadas Longas e RD 3 de armadura. Para seguir '
            'a lore, trate as Gridaksma como foices de duas pontas (GdB+2 corte) e a RD como carne morta, não metal.'
        ),
        'ficha': {
            'pontos_base': 120,
            'atributos': {'ST': 12, 'DX': 14, 'IQ': 9, 'HT': 11, 'PV_extra': 2},
            'vantagens': [
                {'nome': 'Ataque Extra', 'custo': 25, 'notas': 'Uma espada em cada mão'},
                {'nome': 'Resistência a Dano', 'custo': 15, 'notas': 'RD 3 (armadura antiga)'},
                {'nome': 'Imunidade a Dor', 'custo': 10},
            ],
            'pericias': [
                {'nome': 'Espada Larga', 'atributo_base': 'DX', 'dificuldade': 'M', 'pontos': 8},
            ],
            'inventario': [
                {'nome': 'Espada Longa', 'quantidade': 2, 'peso': 3.0, 'notas': 'Lâminas antigas e escuras'},
            ],
        },
    },
    {
        'nome': 'Fetch',
        'categoria': 'Feiticeiro',
        'imagem_url': '/static/images/bestiario/fetch.webp',
        'descricao_publica': (
            'Sacerdotisas a serviço de Balor, entre os servos mais mortais do Escuro. Orgulham-se, de um jeito '
            'perturbador, de conseguir sozinhas dizimar legiões de guerreiros veteranos.\n\n'
            'Das mãos em garra lançam raios que arrasam fileiras inteiras e deixam os soldados reduzidos a cascas '
            'carbonizadas e fumegantes. Os mesmos raios desviam flechas no ar e detonam cargas de pólvora antes '
            'da hora. Andam atrás das hordas de mortos-vivos e as comandam.\n\n'
            'Vestem a pele dos homens que eletrocutaram, como troféu e como aviso. Ninguém sabe o que existe por '
            'baixo: quando uma Fetch morre, algo sobe aos céus como um fantasma e deixa para trás só a pele podre. '
            'Dizem que não são deste mundo.\n\n'
            'Quando uma Fetch aparece, a ordem é espalhar.\n\n'
            '"Não sabemos se as Fetch vestem a pele dos homens por necessidade ou por capricho, mas sabemos que '
            'não são do nosso mundo, e sua arrogância não tem igual entre os servos dos Caídos."\n\n'
            '"Quando a vi pela primeira vez, pensei que fosse um demônio; quando falou, falou com a voz de um anjo. '
            'Mas sua verdadeira natureza estava escondida sob a pele infestada de piolhos que vestia."'
        ),
        'descricao_mestre': (
            'ORIGEM: são sacerdotisas de outro mundo, invocadas por Balor por causa de seus poderes mágicos. '
            'Balor prometeu mandá-las de volta para casa depois da guerra. Vestem peles humanas por necessidade, '
            'não por capricho: se o olho de Wyrd as visse sem disfarce, reconheceria que são estranhas a este '
            'mundo e as destruiria. A verdadeira forma delas nunca é descrita. Odeiam este mundo e todos nele.\n\n'
            'FUTURO (não revelar): depois da derrota de Balor, ficam presas num mundo que desprezam. Seguem '
            'Soulblighter na segunda guerra, esperando que ele cumpra a promessa de Balor. Com a morte de '
            'Soulblighter pelas mãos de Alric, as Fetch que restam perdem qualquer meio de voltar.\n\n'
            'GANCHO: a promessa de Balor é a única coisa que elas realmente querem. Uma Fetch acuada pode '
            'negociar, mentir ou trair por uma chance de voltar para casa.\n\n'
            'REGRAS: Raio: 3d de queimadura, salta para até 2 alvos a 2 m um do outro; precisa de 3 turnos entre '
            'um raio e outro. O raio pode desviar flechas e detonar explosivos no caminho. Sofre só 1/4 do dano '
            'de eletricidade. Muito frágil em corpo a corpo. Alvo prioritário de arqueiros e do berserker.'
        ),
        'ficha': {
            'pontos_base': 120,
            'atributos': {'ST': 9, 'DX': 11, 'IQ': 13, 'HT': 10},
            'vantagens': [
                {'nome': 'Aptidão Mágica', 'custo': 15, 'notas': 'Nível 3'},
                {'nome': 'Raio', 'custo': 30, 'notas': '3d queimadura, salta para 2 alvos; 3 turnos de recarga'},
                {'nome': 'Visão Noturna', 'custo': 1},
            ],
            'pericias': [
                {'nome': 'Ocultismo', 'atributo_base': 'IQ', 'dificuldade': 'M', 'pontos': 4},
                {'nome': 'Furtividade', 'atributo_base': 'DX', 'dificuldade': 'M', 'pontos': 1},
            ],
        },
    },
    {
        'nome': 'Trow',
        'categoria': 'Gigante',
        'descricao_publica': (
            'Gigantes de pedra das lendas antigas, maiores que uma casa. As histórias contam que construíram cidades '
            'no Norte antes dos homens e que dormem há séculos. Ninguém vivo afirma ter visto um.'
        ),
        'descricao_mestre': (
            'Nesta época são só lenda. Use apenas se quiser apresentá-los mais tarde. '
            'Um chute derruba uma fileira inteira; quase impossíveis de matar sem explosivos.'
        ),
        'ficha': {
            'pontos_base': 200,
            'atributos': {'ST': 30, 'DX': 10, 'IQ': 9, 'HT': 13},
            'vantagens': [
                {'nome': 'Resistência a Dano', 'custo': 20, 'notas': 'RD 4 (pele de pedra)'},
            ],
            'pericias': [
                {'nome': 'Briga', 'atributo_base': 'DX', 'dificuldade': 'F', 'pontos': 4},
            ],
        },
    },
]
