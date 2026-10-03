# ==========================================
# Bestiário do Escuro (Myth, ano 17) - adaptação própria para GURPS 4e
# descricao_publica: o que um soldado da Legião sabe. descricao_mestre: só o mestre.
# Todas começam bloqueadas; o mestre revela no site quando o grupo encontra a criatura.
# ==========================================

CRIATURAS = [
    {
        'nome': 'Thrall',
        'categoria': 'Morto-vivo',
        'imagem_url': '/static/images/bestiario/thrall.png',
        'galeria': ['/static/images/bestiario/thrall_bando.png'],
        'descricao_publica': (
            'Cadáveres reanimados de homens que lutaram contra os Senhores Caídos e perderam. São o soldado de '
            'infantaria básico do Escuro e, de longe, o mais numeroso. Por estarem mortos, são lentíssimos, mas '
            'aguentam uma quantidade enorme de golpes antes que a feitiçaria imunda que os mantém de pé se desfaça.\n\n'
            'Qualquer cadáver bem conservado pode virar um Thrall, não importa há quanto tempo esteja morto. Por '
            'isso os necromantes saqueiam criptas, catacumbas e mausoléus antigos para engrossar seus exércitos. '
            'Corpos frescos servem do mesmo jeito: para desespero da Legião, os Senhores Caídos costumam recrutar '
            'entre os inimigos que acabaram de matar, e chegam a atacar vilas sem importância só para "alistar" à '
            'força os moradores. Cada Thrall recebe um machado e uma armadura rudimentar e segue para cumprir seu '
            'papel de carrasco cambaleante.\n\n'
            'Obedecem a ordens simples, mas não pensam. Não entendem flanqueamento nem qualquer tática mais '
            'complicada do que atacar o inimigo mais próximo. Por isso os comandantes do Escuro os lançam em ondas '
            'enormes, contando vencer pelo número, sabendo que cada soldado que cai do outro lado vai engrossar suas '
            'fileiras. Lentos e desajeitados, carregam machados grandes para causar o máximo de dano a cada golpe. '
            'Não sentem dor nem medo. Dizem que atravessam rios andando pelo fundo.\n\n'
            '"...o Vigia esporeou seu exército com um vento escaldante. Três dias inteiros antes da chegada do '
            'exército... os cidadãos de Tyr sabiam que sua ruína se aproximava, arrastando-se, a cada hora que '
            'passava..."\n\n'
            '"...atacaram a cidade de Covenant... reforçados não só pelos camponeses e moradores massacrados... mas '
            'também pelo saque de catacumbas, criptas e cemitérios de mil anos."'
        ),
        'descricao_mestre': (
            'CRIAÇÃO: são os mortos-vivos mais fáceis de fazer. Não exigem um tipo específico de cadáver (como os '
            'Ghasts e, por extensão, os Wights) nem grande esforço do invocador (como os Soulless). Uma vila que o '
            'grupo não conseguir proteger vira, dias depois, uma coluna de Thralls com rostos conhecidos. Bom gancho '
            'para Crow\'s Bridge.\n\n'
            'O VIGIA: os Thralls são a especialidade do Vigia (Bahl\'al). Ele desceu aos salões alagados e '
            'enferrujados de Si\'anwon e, sob o mar, ficou nove dias sem respirar, vasculhando os palácios e templos '
            'arruinados dos Trow em busca do sonho da não-vida. Os mortos dele também não respiram.\n\n'
            '"...a sétima onda de Thralls tropeçou e escalou os mortos empilhados e escorregadios, e Mazzarin viu o '
            'Vigia com eles e enfim soube o número de seus dias."\n\n'
            'HISTÓRIA ANTIGA (Era do Lobo): "Os homens de Dru\'Cullah fizeram sua última resistência contra o '
            'exército do Vigia. Quando o dia raiou, uma massa ondulante surgiu no horizonte: não era o calor do sol '
            'subindo do vale, mas um mar de cadáveres imortais arrastando-se rumo a Dru\'Cullah. A população das '
            'vilas vizinhas tinha engrossado as fileiras dos mortos. Muitos soldados tiraram a própria vida, mas ao '
            'fim do dia todos marchavam para o Vigia."\n\n'
            '"...de cada túmulo, de cada dólmen, de cada mausoléu, os mortos foram levados. Os santuários mais '
            'sagrados foram profanados enquanto os corpos eram carregados em grandes carroças, empilhados e '
            'zumbindo de moscas. Eram despejados aos pés de Bahl\'al e, em minutos, os mortos antigos abriam caminho '
            'com as garras pela massa de cadáveres que se contorcia."\n\n'
            'TÁTICA: atacam em massa. Fogo e explosivos são a melhor resposta. Não reagem a manobras: flanquear e '
            'segurar terreno alto funciona. Não respiram: podem surgir de dentro da água em vaus e margens. '
            'Deslocamento baixo; um grupo móvel consegue fugir deles.\n\n'
            'REGRAS: machado grande (GdB+2 corte). Paralisia (gás do Wight) dura metade do tempo neles. Imunes a '
            'gases e confusão.'
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
        'imagem_url': '/static/images/bestiario/wight.png',
        'descricao_publica': (
            'Um cadáver costurado, trazido de volta por magia sombria para servir de criadouro de doenças virulentas '
            'e podridão imunda. São as tropas suicidas do Escuro. O Wight se arrasta até o alvo e crava uma adaga '
            'no próprio corpo cheio de gás, que explode.\n\n'
            'A explosão paralisa quase tudo o que estiver perto. Os casacos dos Jornadeiros protegem contra isso, e '
            'ninguém sabe bem por quê. Pior que a explosão é o que vem depois: a carne podre deles carrega a febre da '
            'morte sangrenta, uma morte lenta que espera muitos dos que sobrevivem à batalha.\n\n'
            'Não atacam por maldade. O que os empurra para frente é a esperança, turvada pela dor, de se libertar de '
            'uma agonia tão terrível que tortura o corpo deles mesmo depois da morte. Os veteranos repetem: mate-os '
            'de longe.\n\n'
            '"...embora os anões diante de Myrgard não tenham se abalado com os Wights à sua frente, cada um sabia da '
            'lenta febre da morte sangrenta que aguardava os que sobrevivessem à batalha."\n\n'
            '"...antes do ataque a Covenant... quarenta e nove Wights foram tocados para dentro do Tiber, a uma hora '
            'de marcha da cidade, e ficaram ali parados até estourar, deixando a água impossível de beber."'
        ),
        'descricao_mestre': (
            'ORIGEM: o primeiro foi criado pelo necromante Culwyeh, por vingança contra quem tentou matá-lo na Grande '
            'Purificação, quando todo suspeito de praticar necromancia era arrastado aos gritos para a fogueira. '
            'Culwyeh escapou por pouco, fugiu para um pântano fétido e levou anos até dar vida ao seu primeiro '
            '"Mensageiro". O nome Mensageiros de Culwyeh hoje só é lembrado pelos estudiosos mais devotos da '
            'necromancia; um NPC que use esse nome se entrega como iniciado.\n\n'
            'COMO SÃO FEITOS: começam como Ghasts. No peito e na barriga do cadáver escolhido enfiam uma mistura de '
            'esterco, pólipos noturnos e larvas de mosca Kzir; a cavidade é costurada bem apertada e o cadáver '
            'recebe o Sonho da Não-Vida. Depois fica numa jaula, amadurecendo por pelo menos duas luas, com muito '
            'cuidado para não ser ferido. O fungo se alimenta da carne podre e produz um gás tóxico que impregna '
            'músculo, poros e osso; só a pele esticada e inflada segura o gás. Um covil de necromante com jaulas de '
            'Wights "amadurecendo" é um ótimo cenário: qualquer golpe errado detona a sala.\n\n'
            'TÁTICA: andam devagar e têm pouca vida. Arqueiros e o Fir\'Bolg resolvem de longe. O Jornadeiro pode '
            'chegar perto. Use para punir quem avança sem pensar e para envenenar poços e rios antes de um cerco.\n\n'
            'REGRAS: quando chega ao lado de um alvo, se apunhala e explode. Também explode se receber dano de corte '
            'ou perfuração, ou ao morrer. Explosão: 3d esmagamento a até 2 m, e todos na área fazem HT-3 ou ficam '
            'paralisados por 1d minutos. Mortos-vivos e Jornadeiros (pelo casaco) não são paralisados. Febre da morte '
            'sangrenta: quem foi atingido pela explosão faz HT depois da luta; se falhar, perde 1 PV por dia e sangra '
            'pelos olhos e gengivas até ser tratado por um Jornadeiro. Imune a paralisia, gases e confusão.'
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
        'imagem_url': '/static/images/bestiario/trow.png',
        'galeria': ['/static/images/bestiario/trow_montanha.png', '/static/images/bestiario/trow_ruinas.png'],
        'descricao_publica': (
            'Relíquias de uma era esquecida. Os Trow são gigantes maiores que uma casa, que estão no mundo desde o '
            'começo, criados pela deusa Nyx. No auge de sua era dourada ergueram as enormes estruturas de pedra '
            'cujas ruínas ainda se veem pelo mundo, e dizem que as primeiras construções em terra foram obra deles.\n\n'
            'As lendas contam que foram o povo mais cruel que já existiu. Nyx lhes ensinou o segredo do ferro e, '
            'com armas e armaduras forjadas nele, ficaram quase invencíveis. Exterminaram os Sileh\'hei até o último, '
            'expulsaram os Gigantes da Floresta e transformaram a floresta deles num pântano envenenado, escravizaram '
            'os Oghres e tiraram os Fir\'Bolg de suas florestas. Dizem que até o Grande Vazio nasceu da guerra deles '
            'contra os Callieach.\n\n'
            'Na Era do Vento, Connacht derreteu as cidades de ferro dos Trow com o Martelo do Sol e aprisionou os '
            'gigantes sob o metal derretido, para que nunca mais fizessem mal a outro povo. Desde então são só '
            'histórias contadas ao pé do fogo.\n\n'
            'Mesmo assim, nesta guerra, alguns veteranos juram ter visto silhuetas enormes marchando atrás das hordas '
            'do Escuro. Ninguém nas fileiras acredita, ou quer acreditar.\n\n'
            'As lendas lhes dão nomes antigos, numa língua que soa como a dos eruditos: Igne Ferroque, Saxum Pugnus, '
            'Mons Latus, Terramotus Calcitrare, Pulvis Ira.\n\n'
            '"No começo achamos que o celeiro onde nos escondíamos tinha sumido por magia, mas então vimos a silhueta '
            'inconfundível de um Trow ficando cada vez mais nítida através da poeira que baixava..."'
        ),
        'descricao_mestre': (
            'A VERDADE NESTE ANO: os boatos são verdadeiros. Balor libertou os Trow do ferro derretido e ganhou a '
            'lealdade deles; hoje lideram exércitos do Escuro. O primeiro encontro deve ser um choque. Cuidado: quem '
            'os prendeu foi Connacht e quem os soltou foi Balor. Não ligue os dois antes da batalha final.\n\n'
            'ERA DOS TROW: contra os Sileh\'hei, pediram ajuda a Nyx e receberam o ferro. Com o ferro construíram '
            'cidades-templo para ela. Quando as minas acabaram, invadiram a floresta dos Gigantes da Floresta, que '
            'virou o Pântano Funesto; os Gigantes avisaram que os Trow tinham envenenado a alma do ferro. Depois '
            'tomaram à força as Pedras Rúnicas de Wyrd dos Callieach e as levaram para Si\'anwon. Os Callieach '
            'afundaram Si\'anwon no Grande Mar com um terremoto (é nessas ruínas que o Vigia passou nove dias sem '
            'respirar). Os Trow então exterminaram os Callieach; os últimos fugiram para o leste e, em vez de morrer, '
            'destruíram a si mesmos e aos perseguidores num cataclismo. O resultado é o Grande Vazio.\n\n'
            'ERA DO MACHADO: os Oghres chamaram os Trow de "Consortes de Nyx". Os Trow, ofendidos, os escravizaram '
            'para minerar ferro e erguer templos à deusa. Na busca por ferro, expulsaram os Fir\'Bolg da floresta '
            'natal: primeiro para as colinas do Império de Cath Bruig, depois para além da Cloudspine, até a floresta '
            'Ermine. Gancho para um PC Fir\'Bolg.\n\n'
            'ERA DO VENTO: os Oghres se revoltaram com a ajuda de Connacht. No Vale do Selo Vermelho os Trow os '
            'exterminaram, e o sangue manchou as paredes do vale para sempre. Ali os Trow enxergaram a covardia de '
            'milênios, renegaram o ferro ("uma ferramenta melhor deixada para as raças jovens") e juraram nunca mais '
            'usá-lo. Enfraquecidos, foram aprisionados por Connacht com o Martelo do Sol.\n\n'
            '"...ou derrubaremos o seu povo como uma floresta de pinheiros." Um Ghôl perguntou por que ele tinha '
            'escolhido pinheiros. "Pinheiros, depois de cortados, nunca voltam a crescer", disse o emissário Trow, e '
            'os Ghôls não tiveram resposta além do silêncio.\n\n'
            'FUTURO (não revelar): no fim desta guerra os Trow estão quase extintos e decidem ficar fora das batalhas. '
            'Negam ajuda ao Enganador ("Deixe o ferro descansar e escolha um dentre nós. Pergunte o nome dele e o que '
            'ele te deve.") e aceitam ajudar a Luz por um ano depois de perderem um jogo justo.\n\n'
            'INTERPRETAÇÃO: orgulhosos, antigos e lentos para falar, "cada sílaba o rugido de um oceano". Consideram '
            'todos os outros "raças jovens". Respeitam força e jogos justos; dá para negociar com um Trow, nunca '
            'intimidá-lo.\n\n'
            'TÁTICA: um chute derruba uma fileira inteira. Fogo, explosivos e raios rendem pouco contra eles; o que '
            'funciona é dano físico concentrado, muitos guerreiros ao mesmo tempo e flechas sem parar.\n\n'
            'REGRAS: chute 5d+2 esmagamento, e quem for atingido faz DX ou cai. Sofre metade do dano de fogo e 1/4 do '
            'dano de explosivos e eletricidade. Imune a paralisia. Ao chegar a 1/4 dos PV vira pedra e fica inerte. '
            'Curas só devolvem PV até a metade do máximo. A ficha GURPS ainda não tem essas resistências.'
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
