# ==========================================
# Acervo do manual e o que cada campanha ligou
# ==========================================

import json

from database import Database

CATALOGOS = {
    'pericias': {
        'rotulo': 'Perícias',
        'tabela': 'pericias_catalogo',
        'ligacao': 'campanha_pericia',
        'coluna': 'id_pericia',
        'colunas': (
            ('nome', 'Nome'),
            ('atributo_base', 'Atributo'),
            ('dificuldade', 'Dificuldade'),
            ('custo_texto', 'Custo'),
        ),
        'campos': (
            {'nome': 'nome', 'rotulo': 'Nome'},
            {'nome': 'atributo_base', 'rotulo': 'Atributo', 'opcoes': ('ST', 'DX', 'IQ', 'HT')},
            {'nome': 'dificuldade', 'rotulo': 'Dificuldade', 'opcoes': ('F', 'M', 'D', 'MD')},
            {'nome': 'custo_texto', 'rotulo': 'Custo'},
        ),
        'tela': (
            {'nome': 'nome', 'rotulo': 'Nome'},
            {'nome': 'atributo_base', 'rotulo': 'Atributo', 'opcoes': ('ST', 'DX', 'IQ', 'HT')},
            {'nome': 'dificuldade', 'rotulo': 'Dificuldade', 'opcoes': ('F', 'M', 'D', 'MD')},
            {'nome': 'custo_texto', 'rotulo': 'Custo'},
            {'nome': 'descricao', 'rotulo': 'Descrição', 'tipo': 'longo'},
        ),
    },
    'vantagens': {
        'rotulo': 'Vantagens e desvantagens',
        'tabela': 'vantagens_desvantagens_catalogo',
        'ligacao': 'campanha_vantagem',
        'coluna': 'id_vantagem',
        'colunas': (
            ('nome', 'Nome'),
            ('tipo', 'Tipo'),
            ('custo_base', 'Custo'),
            ('categoria', 'Categoria'),
        ),
        'campos': (
            {'nome': 'nome', 'rotulo': 'Nome'},
            {'nome': 'tipo', 'rotulo': 'Tipo', 'opcoes': ('Vantagem', 'Desvantagem')},
            {'nome': 'custo_base', 'rotulo': 'Custo', 'tipo': 'numero'},
            {'nome': 'categoria', 'rotulo': 'Categoria'},
        ),
        'tela': (
            {'nome': 'nome', 'rotulo': 'Nome'},
            {'nome': 'tipo', 'rotulo': 'Tipo', 'opcoes': ('Vantagem', 'Desvantagem')},
            {'nome': 'custo_base', 'rotulo': 'Custo', 'tipo': 'numero'},
            {'nome': 'custo_texto', 'rotulo': 'Custo em texto'},
            {'nome': 'categoria', 'rotulo': 'Categoria'},
            {'nome': 'descricao', 'rotulo': 'Descrição', 'tipo': 'longo'},
        ),
    },
    'magias': {
        'rotulo': 'Magias',
        'tabela': 'magias_catalogo',
        'ligacao': 'campanha_magia',
        'coluna': 'id_magia',
        'colunas': (
            ('nome', 'Nome'),
            ('escola', 'Escola'),
            ('custo', 'Custo'),
        ),
        'campos': (
            {'nome': 'nome', 'rotulo': 'Nome'},
            {'nome': 'escola', 'rotulo': 'Escola'},
            {'nome': 'custo', 'rotulo': 'Custo'},
        ),
        'tela': (
            {'nome': 'nome', 'rotulo': 'Nome'},
            {'nome': 'escola', 'rotulo': 'Escola'},
            {'nome': 'classe', 'rotulo': 'Classe'},
            {'nome': 'dificuldade', 'rotulo': 'Dificuldade', 'opcoes': ('D', 'MD')},
            {'nome': 'custo', 'rotulo': 'Custo'},
            {'nome': 'tempo', 'rotulo': 'Tempo'},
            {'nome': 'duracao', 'rotulo': 'Duração'},
            {'nome': 'pre_requisitos', 'rotulo': 'Pré-requisitos'},
            {'nome': 'descricao', 'rotulo': 'Descrição', 'tipo': 'longo'},
        ),
    },
    'itens': {
        'rotulo': 'Equipamento à venda',
        'tabela': 'itens_catalogo',
        'ligacao': 'campanha_item',
        'coluna': 'id_item',
        'colunas': (
            ('nome', 'Nome'),
            ('categoria', 'Categoria'),
            ('preco', 'Preço'),
            ('peso', 'Peso'),
        ),
        'campos': (
            {'nome': 'nome', 'rotulo': 'Nome'},
            {'nome': 'categoria', 'rotulo': 'Categoria'},
            {'nome': 'preco', 'rotulo': 'Preço', 'tipo': 'numero'},
            {'nome': 'peso', 'rotulo': 'Peso', 'tipo': 'numero'},
        ),
        'tela': (
            {'nome': 'nome', 'rotulo': 'Nome'},
            {'nome': 'categoria', 'rotulo': 'Categoria'},
            {'nome': 'tipo_item', 'rotulo': 'Tipo', 'opcoes': ('equipamento', 'consumivel', 'outro')},
            {'nome': 'preco', 'rotulo': 'Preço', 'tipo': 'numero'},
            {'nome': 'peso', 'rotulo': 'Peso', 'tipo': 'numero'},
            {'nome': 'dano_bal_mod', 'rotulo': 'Dano BAL', 'tipo': 'numero'},
            {'nome': 'dano_bal_tipo', 'rotulo': 'Tipo BAL'},
            {'nome': 'dano_gdp_mod', 'rotulo': 'Dano GDP', 'tipo': 'numero'},
            {'nome': 'dano_gdp_tipo', 'rotulo': 'Tipo GDP'},
            {'nome': 'rd_mod', 'rotulo': 'RD', 'tipo': 'numero'},
            {'nome': 'rd_tipo', 'rotulo': 'Tipo RD'},
            {'nome': 'descricao', 'rotulo': 'Descrição', 'tipo': 'longo'},
        ),
    },
    'criaturas': {
        'rotulo': 'Bestiário',
        'tabela': 'acervo_criaturas',
        'ligacao': 'campanha_criatura',
        'coluna': 'id_acervo',
        'colunas': (
            ('nome', 'Nome'),
            ('categoria', 'Categoria'),
            ('st', 'ST'),
            ('dx', 'DX'),
            ('iq', 'IQ'),
            ('ht', 'HT'),
            ('custo', 'Custo'),
        ),
        'campos': (
            {'nome': 'nome', 'rotulo': 'Nome'},
            {'nome': 'categoria', 'rotulo': 'Categoria', 'opcoes': ('animal', 'monstro')},
            {'nome': 'st', 'rotulo': 'ST', 'tipo': 'numero'},
            {'nome': 'dx', 'rotulo': 'DX', 'tipo': 'numero'},
            {'nome': 'iq', 'rotulo': 'IQ', 'tipo': 'numero'},
            {'nome': 'ht', 'rotulo': 'HT', 'tipo': 'numero'},
            {'nome': 'custo', 'rotulo': 'Custo', 'tipo': 'numero'},
        ),
        'tela': (
            {'nome': 'nome', 'rotulo': 'Nome'},
            {'nome': 'categoria', 'rotulo': 'Categoria'},
            {'nome': 'st', 'rotulo': 'ST', 'tipo': 'numero'},
            {'nome': 'dx', 'rotulo': 'DX', 'tipo': 'numero'},
            {'nome': 'iq', 'rotulo': 'IQ', 'tipo': 'numero'},
            {'nome': 'ht', 'rotulo': 'HT', 'tipo': 'numero'},
            {'nome': 'vontade', 'rotulo': 'Vontade', 'tipo': 'numero'},
            {'nome': 'percepcao', 'rotulo': 'Percepção', 'tipo': 'numero'},
            {'nome': 'velocidade', 'rotulo': 'Velocidade', 'tipo': 'numero'},
            {'nome': 'esquiva', 'rotulo': 'Esquiva', 'tipo': 'numero'},
            {'nome': 'deslocamento', 'rotulo': 'Deslocamento', 'tipo': 'numero'},
            {'nome': 'tamanho', 'rotulo': 'Tamanho'},
            {'nome': 'peso', 'rotulo': 'Peso'},
            {'nome': 'custo', 'rotulo': 'Custo', 'tipo': 'numero'},
            {'nome': 'caracteristicas', 'rotulo': 'Características', 'tipo': 'longo'},
            {'nome': 'pericias', 'rotulo': 'Perícias', 'tipo': 'longo'},
        ),
    },
}


def _spec(aba):
    spec = CATALOGOS.get(aba)
    if not spec:
        raise KeyError(aba)
    return spec


def _texto(valor):
    texto = ('' if valor is None else str(valor)).strip()
    return texto or None


def _numero(valor, inteiro=True):
    texto = ('' if valor is None else str(valor)).strip().replace(',', '.')
    if not texto:
        return None
    return int(float(texto)) if inteiro else float(texto)


def _ler_ajustes(bruto):
    if not bruto:
        return {}
    if isinstance(bruto, dict):
        return bruto
    try:
        dados = json.loads(bruto)
    except (TypeError, ValueError):
        return {}
    return dados if isinstance(dados, dict) else {}


def _mesmo_valor(original, novo):
    if original is None and novo is None:
        return True
    if original is None or novo is None:
        return False
    try:
        from decimal import Decimal
        if isinstance(original, (int, float, Decimal)) or isinstance(novo, (int, float, Decimal)):
            return Decimal(str(original)) == Decimal(str(novo))
    except Exception:
        pass
    return str(original) == str(novo)


def _misturar(linha):
    efetivo = dict(linha)
    for campo, valor in _ler_ajustes(linha.get('ajustes')).items():
        if campo in efetivo and campo not in ('id', 'origem', 'id_campanha', 'ajustes', 'selecionado'):
            efetivo[campo] = valor
    efetivo.pop('ajustes', None)
    return efetivo


class Acervo:
    @staticmethod
    def abas():
        return tuple(CATALOGOS.items())

    @staticmethod
    def spec(aba):
        return _spec(aba)

    @staticmethod
    def listar_disponiveis(aba, campanha_id, tipo=None):
        if not campanha_id:
            return []
        spec = _spec(aba)
        coluna = spec['coluna']
        filtro = ''
        params = [campanha_id, campanha_id]
        if tipo:
            filtro = ' AND c.tipo = %s'
            params.append(tipo)
        query = f"""
            SELECT c.*, s.ajustes
            FROM {spec['tabela']} c
            LEFT JOIN {spec['ligacao']} s
                ON s.{coluna} = c.id AND s.id_campanha = %s
            WHERE s.{coluna} IS NOT NULL
              AND (c.origem = 'manual' OR c.id_campanha = %s)
            {filtro}
            ORDER BY c.nome
        """
        linhas = Database.execute_query(query, tuple(params)) or []
        return [_misturar(linha) for linha in linhas]

    @staticmethod
    def disponivel(aba, campanha_id, item_id):
        if not campanha_id or not item_id:
            return False
        spec = _spec(aba)
        coluna = spec['coluna']
        query = f"""
            SELECT c.id
            FROM {spec['tabela']} c
            LEFT JOIN {spec['ligacao']} s
                ON s.{coluna} = c.id AND s.id_campanha = %s
            WHERE c.id = %s
              AND s.{coluna} IS NOT NULL
              AND (c.origem = 'manual' OR c.id_campanha = %s)
        """
        return bool(Database.execute_query(query, (campanha_id, item_id, campanha_id)))

    @staticmethod
    def listar_catalogo(aba, campanha_id, so_adicionados=False, busca=''):
        spec = _spec(aba)
        coluna = spec['coluna']
        filtro = ''
        params = [campanha_id, campanha_id]
        termo = (busca or '').strip()
        if termo:
            filtro = 'AND c.nome LIKE %s'
            params.append(f'%{termo}%')
        linhas = Database.execute_query(
            f"""
            SELECT c.*, s.ajustes,
                   CASE WHEN s.{coluna} IS NOT NULL THEN 1 ELSE 0 END AS selecionado
            FROM {spec['tabela']} c
            LEFT JOIN {spec['ligacao']} s
                ON s.{coluna} = c.id AND s.id_campanha = %s
            WHERE (c.origem = 'manual'
               OR (c.origem = 'campanha' AND c.id_campanha = %s))
            {filtro}
            ORDER BY c.nome
            """,
            tuple(params),
        ) or []
        prontas = []
        for linha in linhas:
            if bool(linha.get('selecionado')) != so_adicionados:
                continue
            linha['efetivo'] = _misturar(linha)
            prontas.append(linha)
        return prontas

    @staticmethod
    def registro_efetivo(aba, campanha_id, item_id):
        spec = _spec(aba)
        coluna = spec['coluna']
        linhas = Database.execute_query(
            f"""
            SELECT c.*, s.ajustes
            FROM {spec['tabela']} c
            LEFT JOIN {spec['ligacao']} s
                ON s.{coluna} = c.id AND s.id_campanha = %s
            WHERE c.id = %s
              AND s.{coluna} IS NOT NULL
              AND (c.origem = 'manual' OR c.id_campanha = %s)
            """,
            (campanha_id, item_id, campanha_id),
        )
        return _misturar(linhas[0]) if linhas else None

    @staticmethod
    def adicionar_a_campanha(aba, campanha_id, item_id):
        spec = _spec(aba)
        item = Acervo._buscar(spec, item_id)
        if not item:
            return False
        if item.get('origem') == 'campanha' and item.get('id_campanha') != campanha_id:
            return False
        coluna = spec['coluna']
        Database.execute_query(
            f"INSERT IGNORE INTO {spec['ligacao']} (id_campanha, {coluna}) VALUES (%s, %s)",
            (campanha_id, item_id),
            fetch=False,
        )
        if aba == 'criaturas':
            Acervo._garantir_bestiario(campanha_id, item)
        return True

    @staticmethod
    def salvar_ajustes(aba, campanha_id, item_id, formulario):
        spec = _spec(aba)
        item = Acervo._buscar(spec, item_id)
        if not item or not Acervo.disponivel(aba, campanha_id, item_id):
            return False
        ajustes = {}
        for campo in spec['tela']:
            nome = campo['nome']
            if nome not in formulario:
                continue
            bruto = formulario.get(nome)
            if campo.get('opcoes'):
                valor = bruto if bruto in campo['opcoes'] else item.get(nome)
            elif campo.get('tipo') == 'numero':
                valor = _numero(bruto, inteiro=campo['nome'] not in ('preco', 'peso', 'velocidade'))
            else:
                valor = _texto(bruto) if bruto is not None else None
            original = item.get(nome)
            if _mesmo_valor(original, valor):
                continue
            ajustes[nome] = valor
        coluna = spec['coluna']
        Database.execute_query(
            f"UPDATE {spec['ligacao']} SET ajustes = %s WHERE id_campanha = %s AND {coluna} = %s",
            (json.dumps(ajustes, ensure_ascii=False) if ajustes else None, campanha_id, item_id),
            fetch=False,
        )
        return True

    @staticmethod
    def restaurar_ajustes(aba, campanha_id, item_id):
        spec = _spec(aba)
        coluna = spec['coluna']
        Database.execute_query(
            f"UPDATE {spec['ligacao']} SET ajustes = NULL WHERE id_campanha = %s AND {coluna} = %s",
            (campanha_id, item_id),
            fetch=False,
        )

    @staticmethod
    def remover_da_campanha(aba, campanha_id, item_id):
        spec = _spec(aba)
        coluna = spec['coluna']
        Database.execute_query(
            f"DELETE FROM {spec['ligacao']} WHERE id_campanha = %s AND {coluna} = %s",
            (campanha_id, item_id),
            fetch=False,
        )
        return True

    @staticmethod
    def _ligar_por_nome(aba, campanha_id, nome):
        spec = _spec(aba)
        linhas = Database.execute_query(
            f"SELECT id FROM {spec['tabela']} WHERE nome = %s",
            (nome,),
        )
        if linhas:
            Acervo.adicionar_a_campanha(aba, campanha_id, linhas[0]['id'])

    @staticmethod
    def criar(aba, campanha_id, dados):
        nome = _texto(dados.get('nome'))
        if not nome:
            raise ValueError('Nome é obrigatório.')
        if aba == 'pericias':
            Acervo._inserir_pericia(campanha_id, nome, dados)
            Acervo._ligar_por_nome('pericias', campanha_id, nome)
        elif aba == 'vantagens':
            Acervo._inserir_vantagem(campanha_id, nome, dados)
            Acervo._ligar_por_nome('vantagens', campanha_id, nome)
        elif aba == 'magias':
            Acervo._inserir_magia(campanha_id, nome, dados)
            Acervo._ligar_por_nome('magias', campanha_id, nome)
        elif aba == 'itens':
            Acervo._inserir_item(campanha_id, nome, dados)
            Acervo._ligar_por_nome('itens', campanha_id, nome)
        elif aba == 'criaturas':
            item_id = Acervo._inserir_criatura(campanha_id, nome, dados)
            Database.execute_query(
                "INSERT IGNORE INTO campanha_criatura (id_campanha, id_acervo) VALUES (%s, %s)",
                (campanha_id, item_id),
                fetch=False,
            )
            criada = Acervo._buscar(_spec('criaturas'), item_id)
            Acervo._garantir_bestiario(campanha_id, criada)
        else:
            raise KeyError(aba)

    @staticmethod
    def _buscar(spec, item_id):
        result = Database.execute_query(
            f"SELECT * FROM {spec['tabela']} WHERE id = %s",
            (item_id,),
        )
        return result[0] if result else None

    @staticmethod
    def _inserir_pericia(campanha_id, nome, dados):
        atributo = dados.get('atributo_base') or 'DX'
        dificuldade = dados.get('dificuldade') or 'M'
        if atributo not in ('ST', 'DX', 'IQ', 'HT'):
            raise ValueError('Atributo inválido.')
        if dificuldade not in ('F', 'M', 'D', 'MD'):
            raise ValueError('Dificuldade inválida.')
        Database.execute_query(
            """
            INSERT INTO pericias_catalogo
                (nome, atributo_base, dificuldade, custo_texto, origem, id_campanha)
            VALUES (%s, %s, %s, %s, 'campanha', %s)
            """,
            (nome, atributo, dificuldade, {'F': '1', 'M': '3', 'D': '7', 'MD': '15'}[dificuldade], campanha_id),
            fetch=False,
        )

    @staticmethod
    def _inserir_vantagem(campanha_id, nome, dados):
        tipo = dados.get('tipo') or 'Vantagem'
        if tipo not in ('Vantagem', 'Desvantagem'):
            raise ValueError('Tipo inválido.')
        custo = _numero(dados.get('custo_base'))
        if custo is None:
            raise ValueError('Custo é obrigatório.')
        Database.execute_query(
            """
            INSERT INTO vantagens_desvantagens_catalogo
                (nome, tipo, custo_base, categoria, origem, id_campanha)
            VALUES (%s, %s, %s, %s, 'campanha', %s)
            """,
            (nome, tipo, custo, _texto(dados.get('categoria')), campanha_id),
            fetch=False,
        )

    @staticmethod
    def _inserir_magia(campanha_id, nome, dados):
        escola = _texto(dados.get('escola'))
        if not escola:
            raise ValueError('Escola é obrigatória.')
        Database.execute_query(
            """
            INSERT INTO magias_catalogo
                (nome, escola, custo, origem, id_campanha)
            VALUES (%s, %s, %s, 'campanha', %s)
            """,
            (nome, escola, _texto(dados.get('custo')), campanha_id),
            fetch=False,
        )

    @staticmethod
    def _inserir_item(campanha_id, nome, dados):
        preco = _numero(dados.get('preco'), inteiro=False)
        peso = _numero(dados.get('peso'), inteiro=False)
        Database.execute_query(
            """
            INSERT INTO itens_catalogo
                (nome, categoria, preco, peso, tipo_item, origem, id_campanha)
            VALUES (%s, %s, %s, %s, 'equipamento', 'campanha', %s)
            """,
            (nome, _texto(dados.get('categoria')), preco or 0, peso or 0, campanha_id),
            fetch=False,
        )

    @staticmethod
    def _inserir_criatura(campanha_id, nome, dados):
        categoria = dados.get('categoria') or 'monstro'
        if categoria not in ('animal', 'monstro'):
            raise ValueError('Categoria inválida.')
        return Database.execute_query(
            """
            INSERT INTO acervo_criaturas
                (nome, categoria, st, dx, iq, ht, custo, origem, id_campanha)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'campanha', %s)
            """,
            (
                nome,
                categoria,
                _numero(dados.get('st')),
                _numero(dados.get('dx')),
                _numero(dados.get('iq')),
                _numero(dados.get('ht')),
                _numero(dados.get('custo')),
                campanha_id,
            ),
            fetch=False,
        )

    @staticmethod
    def _garantir_bestiario(campanha_id, criatura):
        from models.bestiario import Bestiario

        existe = Database.execute_query(
            "SELECT id FROM bestiario WHERE id_campanha = %s AND nome = %s",
            (campanha_id, criatura['nome']),
        )
        if existe:
            return
        partes = []
        for rotulo, campo in (
            ('ST', 'st'), ('DX', 'dx'), ('IQ', 'iq'), ('HT', 'ht'),
            ('Vontade', 'vontade'), ('Percepção', 'percepcao'),
            ('Velocidade', 'velocidade'), ('Esquiva', 'esquiva'),
            ('Deslocamento', 'deslocamento'), ('Custo', 'custo'),
        ):
            if criatura.get(campo) is not None:
                partes.append(f'{rotulo} {criatura[campo]}')
        if criatura.get('caracteristicas'):
            partes.append(criatura['caracteristicas'])
        if criatura.get('pericias'):
            partes.append(criatura['pericias'])
        Bestiario.criar({
            'id_campanha': campanha_id,
            'nome': criatura['nome'],
            'categoria': criatura.get('categoria'),
            'descricao_publica': None,
            'descricao_mestre': '. '.join(partes) or None,
            'imagem_url': None,
            'ficha_personagem_id': None,
            'nivel_revelacao': Bestiario.OCULTA,
        })
