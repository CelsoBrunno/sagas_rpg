# ==========================================
# Dados da campanha Myth - ano 17 da Grande Guerra (Myth: The Fallen Lords)
# ==========================================
# Campos públicos: só o que um soldado da Legião sabe no início do ano 17.
# Campos de mestre: revelações posteriores, com o momento em que acontecem.

RACAS = [
    {
        'nome': 'Humano',
        'descricao': 'Povo da Província e das Cidades Livres do Norte. Formam o grosso da Legião.',
        'custo_em_pontos': 0,
        'observacoes': 'Sem modificadores. Escolha natural para guerreiros, berserkers e jornadeiros.',
    },
    {
        'nome': 'Anão',
        'descricao': (
            'Refugiados de Myrgard e Stoneheim, expulsos pelos Ghôls há cinquenta anos. '
            'Fortes, teimosos e famosos pelo uso de pólvora.'
        ),
        'bonus_st': 1,
        'bonus_ht': 1,
        'custo_em_pontos': 20,
        'observacoes': 'Baixa estatura. Ódio antigo aos Ghôls. Sugestão: perícia Explosivos.',
    },
    {
        'nome': "Fir'Bolg",
        'descricao': (
            'Povo das florestas, antigos inimigos dos humanos, aliados agora contra os Senhores Caídos. '
            'Arqueiros de mira lendária, fracos no corpo a corpo.'
        ),
        'bonus_st': -1,
        'bonus_dx': 1,
        'bonus_percepcao_extra': 2,
        'custo_em_pontos': 20,
        'observacoes': 'Desconfiança mútua com humanos mais velhos. Sugestão: perícias Arco e Sobrevivência (Floresta).',
    },
]

CLASSES = [
    {
        'nome': 'Guerreiro',
        'descricao': 'Soldado das Cidades Livres: espada longa, escudo e cota de malha. Sobreviveu a outros encontros com o Escuro.',
        'bonus_st': 1,
        'bonus_pv_extra': 2,
        'custo_em_pontos': 15,
        'observacoes': 'Perícias sugeridas: Espada Larga, Escudo. Equipamento inicial: espada longa, escudo, cota de malha.',
    },
    {
        'nome': 'Berserker',
        'descricao': 'Guerreiro do Norte (Gower e os Doze Duns). Sem armadura, claymore nas mãos, o mais rápido da Luz. Rival jurado dos Myrmidons.',
        'bonus_st': 1,
        'bonus_pf_extra': 2,
        'custo_em_pontos': 15,
        'observacoes': 'Desvantagem sugerida: Fúria (Berserk). Perícias sugeridas: Espada de Duas Mãos, Rastreamento.',
    },
    {
        'nome': 'Arqueiro',
        'descricao': 'Atirador de longa distância. Usa flechas incendiárias e uma faca como último recurso.',
        'bonus_percepcao_extra': 2,
        'custo_em_pontos': 10,
        'observacoes': "Perícias sugeridas: Arco, Faca. Combina com a raça Fir'Bolg.",
    },
    {
        'nome': 'Jornadeiro',
        'descricao': (
            'Curandeiro errante. Os Jornadeiros foram a guarda do antigo Império Cath Bruig e vagam em penitência '
            'desde a queda de Muirthemne. Curam com raízes de mandrágora e guardam lendas antigas.'
        ),
        'bonus_vontade_extra': 1,
        'custo_em_pontos': 5,
        'observacoes': 'Perícias sugeridas: Primeiros Socorros, Herbalismo, História. Item: raízes de mandrágora (cura).',
    },
    {
        'nome': 'Granadeiro anão',
        'descricao': 'Especialista anão em cargas de pólvora e frascos incendiários. Devastador à distância, frágil se cercado.',
        'bonus_ht': 1,
        'custo_em_pontos': 10,
        'observacoes': 'Só para a raça Anão (combinado na mesa). Perícias sugeridas: Explosivos, Arremesso.',
    },
]

LOCAIS = [
    {
        'nome': "Crow's Bridge",
        'tipo': 'Vila',
        'descricao_publica': (
            'Vila ao norte de Madrigal, junto a uma ponte de pedra. Está cheia de refugiados que fogem do sul. '
            'A Legião acampa aqui a caminho de Madrigal, que está sob cerco. Os moradores pediram que um '
            'destacamento ficasse para guardar a ponte.'
        ),
        'descricao_mestre': (
            'Primeira cena da campanha. Nesta noite uma força avançada do exército de Shiver ataca a ponte. '
            'Quem ficou para trás precisa segurar até o amanhecer.'
        ),
    },
    {
        'nome': 'Otter Ferry',
        'tipo': 'Vila',
        'descricao_publica': (
            'Vila de balsa entre Crow\'s Bridge e Comfort. Ponto de travessia do rio Meander para quem marcha '
            'rumo a Madrigal. O prefeito recebe a Legião com festa.'
        ),
        'descricao_mestre': (
            'O prefeito negocia em segredo com o Escuro, esperando ser poupado quando Madrigal cair. '
            'Ele marca um encontro com batedores inimigos para entregar a rota da Legião.'
        ),
    },
    {
        'nome': 'Madrigal',
        'tipo': 'Cidade',
        'descricao_publica': (
            'A última grande cidade livre e sede dos Nove. O Portão das Tempestades é sua entrada principal. '
            'Está cercada pelo exército de Shiver. Se Madrigal cair, a guerra acaba.'
        ),
        'descricao_mestre': (
            'O cerco é quebrado por um movimento de pinça: a Legião ataca por fora e a guarnição sai pelos portões. '
            'Na primeira noite, Rabican mata Shiver num duelo de sonho, graças ao conselho da Cabeça sobre a vaidade dela. '
            'Mais adiante na guerra, a discórdia causada pela Cabeça e o peso dos exércitos do leste derrubam a cidade, '
            'semanas antes do fim.'
        ),
    },
    {
        'nome': 'Comfort',
        'tipo': 'Ruína',
        'descricao_publica': (
            'Vila em ruínas a leste de Madrigal. Hoje é o acampamento-base do exército de Shiver.'
        ),
        'descricao_mestre': (
            'Um pequeno grupo da Legião entra em Comfort para atrair parte do exército de Shiver para longe '
            'da batalha principal. É a missão que equilibra as chances em Madrigal.'
        ),
    },
    {
        'nome': 'Covenant',
        'tipo': 'Ruína',
        'descricao_publica': (
            'Antiga grande cidade da Província, onde ficava a Grande Universidade. Caiu para o Escuro há doze anos. '
            'Seus sobreviventes fugiram para as Cidades Livres do Norte. Hoje é um lugar de mortos.'
        ),
        'descricao_mestre': (
            'Na catedral está o Total Codex, livro que contém passado, presente e futuro. Uma primeira expedição, '
            'liderada por Mauriac, foi enviada para buscá-lo e desapareceu. Os sobreviventes resistem na catedral. '
            'O Vigia está a caminho para tomar o Codex. Há um túnel secreto até a cidade de Shoal, o mesmo por onde '
            'Alric fugiu criança. Soulblighter observa tudo de longe. Quem abrir o Codex lê sobre um homem que '
            'trará de volta os Myrkridia (presságio do segundo jogo, não explicar).'
        ),
    },
    {
        'nome': 'Tyr',
        'tipo': 'Ruína',
        'descricao_publica': (
            'Grande cidade da Província, destruída há doze anos pelo exército do Vigia, no mesmo ano em que caiu Covenant.'
        ),
        'descricao_mestre': (
            'Durante a queda de Tyr, o Vigia e o Enganador travaram um duelo de sonho entre si. O Enganador venceu e o '
            'Vigia mal sobreviveu. A rivalidade entre os dois é antiga, anterior a Balor. Isso será útil mais tarde.'
        ),
    },
    {
        'nome': 'Cordilheira Cloudspine',
        'tipo': 'Montanha',
        'descricao_publica': (
            'Cadeia de montanhas que separa a Província do leste dominado pelo Escuro. Os passos de Seven Gates '
            '(centro) e Bagrada (sul) são as únicas rotas para um grande exército. A neve do inverno fecha os dois.'
        ),
        'descricao_mestre': (
            'O exército do Enganador se prepara para cruzar e substituir as forças de Shiver no oeste. '
            'Os Nove precisam segurar os passos até a neve. Atrás das linhas há um Nó do Mundo (transporte mágico) '
            'que o inimigo pode usar. O vulcão Tharsis, sobre Seven Gates, entrará em erupção pela primeira vez em mil anos, '
            'derreterá a neve e abrirá a passagem.'
        ),
    },
    {
        'nome': 'A Barreira',
        'tipo': 'Montanha',
        'descricao_publica': (
            'Terra de rochas e desertos muito a leste, além da Cloudspine, em território do Escuro. '
            'Poucos que vão até lá voltam.'
        ),
        'descricao_mestre': (
            'Foi na Barreira que Truan das Cem Batalhas encontrou a Cabeça enterrada, ainda viva. '
            'É também lá que a Cabeça manda Alric procurar uma armadura encantada, o que é uma armadilha: '
            'Alric será capturado pelo Enganador e seu exército do leste será destruído.'
        ),
    },
    {
        'nome': 'Muirthemne',
        'tipo': 'Cidade',
        'imagem_principal_url': '/static/images/locais/muirthemne.jpg',
        'descricao_publica': (
            'Antiga capital do Império Cath Bruig. Antes se chamava Llancarfan. Connacht mudou o nome para homenagear '
            'os ferreiros anões que ajudaram a defendê-la. Foi a cidade dos grandes feiticeiros e artesãos do império, '
            'e as lendas dizem que o Martelo do Sol foi forjado ali. O Escuro, comandado por Balor, cercou e saqueou '
            'a cidade, e hoje só restam ruínas no meio da Barreira. Os veteranos dizem que os mortos ainda andam '
            'pelas praças e que quase ninguém que entra volta.'
        ),
        'descricao_mestre': (
            'Foi nestas ruínas que Truan das Cem Batalhas, a pedido de Alric, desenterrou a Cabeça ainda viva. '
            'O Tain também foi feito aqui, por artesãos do Cath Bruig. '
            'Balor saqueou a cidade que ele mesmo governou quando era Connacht. Não ligar os dois antes da batalha final.\n\n'
            'FUTURO (Segunda Guerra, décadas depois): Alric manda a Legião retomar a cidade. Morteiros anões e quatro Trow '
            'rompem as forças de Herod, a Legião entra no mausoléu assombrado atrás da coroa e Alric é coroado imperador '
            'do Cath Bruig. A Guarda Garça renasce e repele um cerco de Myrkridia e gigantes mandado pelo Enganador.'
        ),
    },
    {
        'nome': 'Império Cath Bruig',
        'tipo': 'Outro',
        'descricao_publica': (
            'O maior império humano da história, hoje só lembrado em lendas. Foi fundado pelo imperador Clovis no '
            'início da Era da Razão, com capital em Llancarfan, depois chamada Muirthemne. Clovis fez alianças com os '
            'anões e com os Skrael. O terceiro imperador, Folsom, criou a Guarda Garça, soldados de elite que davam a '
            'vida pelo império. O império expulsou os fir\'Bolg das terras das Colinas para a floresta Ermine.\n\n'
            'Na Era da Razão, a guerra contra o Vigia levou à Grande Purificação, quando nobres fanáticos mandaram '
            'exilar ou executar todo praticante de magia. Na mesma época surgiu o Nivelador Moagim, que soltou os '
            'Myrkridia sobre o mundo e esmagou muitas cidades do império.\n\n'
            'Na Era do Vento, Connacht reuniu os berserkers, expulsou os Myrkridia e passou a comandar os exércitos do '
            'imperador Leitrim. Com Damas, Ravanna e outros heróis, além de anões, Avatara e bruxos, aprisionou os '
            'Myrkridia, conquistou os Trow e venceu o Vigia. Moagim matou Leitrim numa emboscada noturna no Passo Norte, '
            'e Connacht matou Moagim em combate. Connacht virou imperador e deu à capital o nome de Muirthemne, em '
            'honra aos ferreiros anões.\n\n'
            'Mil anos depois, Balor veio do leste e arrasou Muirthemne. Ceiscoran foi o último imperador, e a Coroa '
            'de Íbis se perdeu. A Guarda Garça, envergonhada por deixar o império cair, largou '
            'espadas e armaduras e virou os Jornadeiros.'
        ),
        'descricao_mestre': (
            'O conselheiro imperial de Leitrim era Mjarin, Alto Mestre dos Bruxos de Scholomance. Mjarin era o Nivelador '
            'e armou a morte de Leitrim. Tentou matar Connacht e Damas, e Connacht o decapitou. A cabeça dele é a Cabeça '
            'que Truan trouxe da Barreira.\n\n'
            'Balor é o próprio Connacht, que voltou mil anos depois e destruiu a cidade que governou. '
            'Não revelar antes da batalha final.\n\n'
            'Coroa de Íbis: Ceiscoran mandou fazer onze cópias para dificultar o roubo. A verdadeira está escondida no '
            'mausoléu de Clovis, construído pelos anões em Muirthemne.\n\n'
            'FUTURO (Segunda Guerra): Alric acha a coroa no mausoléu assombrado, que está cheio de Fetch e Myrkridia, e é '
            'coroado imperador. A Guarda Garça volta ao serviço. A coroa multiplica por dez o poder de Alric, '
            'que assim derrota o Enganador.'
        ),
    },
]

# A descrição do mapa é visível para os jogadores
MAPAS = [
    {
        'nome_mapa': 'Mapa-múndi dos Senhores Caídos',
        'url_imagem': '/static/images/mapas/myth_mapa_mundi.png',
        'tipo_mapa': 'Regional',
        'local': None,
        'descricao': (
            'O mundo conhecido no ano 17 da guerra. A oeste, entre o Oceano Ocidental e a Cordilheira Cloudspine, '
            'fica a Província, com Madrigal, Tyr, Covenant e Scales. Ao norte dela, as Cidades Livres do Norte, '
            'com Tandem, Willow, Crow\'s Bridge e Otter Ferry. No centro, a floresta Ermine. A leste da Cloudspine, '
            'passados os passos de Seven Gates e Bagrada, começa a Barreira, o deserto em volta das ruínas de '
            'Muirthemne, já em terras do Escuro. Mais além ficam Forest Heart, os reinos anões de Myrgard e '
            'Stoneheim, o Grande Vazio e, no extremo nordeste, Rhi\'anon. O quadro marcado no oeste é a região '
            'onde a Legião está agora.'
        ),
    },
]

NPCS = [
    {
        'nome': 'Alric',
        'status': 'Vivo',
        'local': None,
        'descricao_breve': (
            'Avatara e líder dos Nove, rei da Província do Sul. Lidera da linha de frente. '
            'Neste momento está no leste com seu exército.'
        ),
        'descricao_completa': (
            'Seguindo o conselho da Cabeça, Alric vai à Barreira atrás de uma armadura encantada e cai numa armadilha. '
            'É capturado e interrogado pelo Enganador; seu exército do leste é aniquilado. Os Cinco Campeões da Legião '
            'o resgatam. No fim do primeiro jogo, Alric mata Balor em Rhi\'anon e manda a cabeça dele ao Grande Vazio. '
            'Só nessa batalha final Alric diz que Balor foi Connacht. Não revelar antes.'
        ),
    },
    {
        'nome': 'Rabican',
        'status': 'Vivo',
        'local': 'Madrigal',
        'descricao_breve': 'Avatara dos Nove, um dos mais poderosos. Comanda a defesa de Madrigal.',
        'descricao_completa': (
            'Vence Shiver num duelo de sonho na primeira noite da batalha de Madrigal, explorando a vaidade dela '
            '(dica da Cabeça). Depois manda a Legião buscar o Codex em Covenant e segura Seven Gates até a neve. '
            'Morre quando Tharsis entra em erupção e o Vigia ataca seu exército pela retaguarda.'
        ),
    },
    {
        'nome': 'Maeldun',
        'status': 'Vivo',
        'local': None,
        'descricao_breve': 'Avatara dos Nove. Comanda a guarnição do sul. Caçou os piratas de Leix que queimaram metade de Tyr.',
        'descricao_completa': (
            'Encontra a Legião nas ruínas de Scales e recebe o Total Codex. Segura o passo de Bagrada até a neve. '
            'Depois da erupção de Tharsis, fecha Seven Gates. É gravemente ferido no último ano da guerra.'
        ),
    },
    {
        'nome': 'Mauriac',
        'status': 'Desconhecido',
        'local': 'Covenant',
        'descricao_breve': (
            'Capitão guerreiro, antigo príncipe regente de Covenant. Famoso por ter matado Fang-Grinder, rei dos Ghôls. '
            'Liderou uma expedição a Covenant e não há notícias dele.'
        ),
        'descricao_completa': (
            'Está vivo, resistindo com poucos sobreviventes na catedral de Covenant. Conhece o túnel secreto até Shoal, '
            'por onde salvou Alric criança quando a cidade caiu.'
        ),
    },
    {
        'nome': 'Balor',
        'status': 'Vivo',
        'local': None,
        'descricao_breve': (
            'Senhor dos Senhores Caídos e comandante dos exércitos do Escuro. Ninguém sabe de onde veio. '
            'Seis feiticeiros-generais o servem.'
        ),
        'descricao_completa': (
            'Foi Connacht, herói da Era do Vento, que matou Moagim. Voltou mil anos depois usando o manto do Nivelador. '
            'Conhece os artefatos de poder porque ele mesmo os escondeu quando era Connacht. '
            'Revelação: só na batalha final do primeiro jogo, numa fala de Alric ouvida por poucos. '
            'A regra de que quem mata o Nivelador vira o próximo só é dita no fim do segundo jogo. Nunca antes.'
        ),
    },
    {
        'nome': 'Shiver',
        'status': 'Vivo',
        'local': 'Comfort',
        'descricao_breve': 'Senhora Caída que comanda o cerco de Madrigal a partir do acampamento em Comfort.',
        'descricao_completa': (
            'Sua fraqueza é a vaidade. Morre na primeira noite da batalha, num duelo de sonho com Rabican. '
            'Na Era do Lobo foi Ravanna, amante e esposa de Damas. Volta no segundo jogo, ressuscitada.'
        ),
    },
    {
        'nome': 'Soulblighter',
        'status': 'Vivo',
        'local': None,
        'descricao_breve': (
            'Senhor Caído e braço direito de Balor. Dizem que é o mais cruel de todos e que foi ele quem saqueou Covenant.'
        ),
        'descricao_completa': (
            'Observa a Legião de longe durante a fuga de Covenant. Boato (nunca confirmado como fato): teria sido Damas, '
            'tenente e melhor amigo de Connacht, que buscou a imortalidade em rituais de automutilação. '
            'É o vilão do segundo jogo e quem traz de volta os Myrkridia.'
        ),
    },
    {
        'nome': 'O Vigia',
        'status': 'Vivo',
        'local': None,
        'descricao_breve': (
            'Senhor Caído e o necromante mais poderoso que já existiu. Destruiu Tyr. Seu exército de mortos '
            'ainda vaga pela Província.'
        ),
        'descricao_completa': (
            'Seu nome é Bahl\'al. Perdeu um braço quando Balor o libertou do cativeiro; o braço está nas ruínas de '
            'Silvermines. É rival antigo do Enganador. Mata Rabican em Seven Gates. A Legião o destrói usando o próprio braço.'
        ),
    },
    {
        'nome': 'O Enganador',
        'status': 'Vivo',
        'local': 'Cordilheira Cloudspine',
        'descricao_breve': 'Senhor Caído cujo exército está a leste da Cloudspine, pronto para cruzar os passos.',
        'descricao_completa': (
            'Foi Myrdred, um Avatara que traiu Connacht, Damas e Ravanna em troca do saber de Mjarin, o Nivelador '
            'da época. Era assistente e espião de Mjarin. Balor o trouxe de volta dos mortos. Não ama nenhum Senhor '
            'Caído e odeia o Vigia. Captura Alric na Barreira. Some depois que o Vigia destrói seu exército em Seven Gates.'
        ),
    },
    {
        'nome': 'A Cabeça',
        'status': 'Vivo',
        'local': 'Madrigal',
        'descricao_breve': (
            'Uma cabeça cortada e viva, encontrada enterrada na Barreira e trazida por Truan das Cem Batalhas. '
            'Diz ser inimiga antiga de Balor. Os Nove ouvem seus conselhos.'
        ),
        'descricao_completa': (
            'É Mjarin, o Nivelador anterior, decapitado por Connacht. Seus conselhos são reais quando servem a ela: '
            'acerta sobre Shiver, mas manda Alric para a armadilha da Barreira. Mais tarde provoca uma guerra civil entre '
            'os Nove e a queda de Madrigal. Sua identidade não deve ser dita aos jogadores.'
        ),
    },
]
