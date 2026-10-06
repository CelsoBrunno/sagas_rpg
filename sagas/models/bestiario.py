# ==========================================
# Bestiário: criaturas da campanha, liberadas pelo mestre
# ==========================================

from database import Database

_CAMPOS = ('nome', 'categoria', 'descricao_publica', 'descricao_mestre',
           'imagem_url', 'ficha_personagem_id', 'nivel_revelacao')


class Bestiario:
    OCULTA = 0
    AVISTADA = 1
    DERROTADA = 2
    NIVEIS = {
        OCULTA: 'Oculta',
        AVISTADA: 'Avistada',
        DERROTADA: 'Derrotada',
    }

    @staticmethod
    def nivel_valido(valor):
        try:
            nivel = int(valor)
        except (TypeError, ValueError):
            return Bestiario.OCULTA
        return nivel if nivel in Bestiario.NIVEIS else Bestiario.OCULTA

    @staticmethod
    def listar_por_campanha(campanha_id):
        query = f"""
            SELECT * FROM bestiario
            WHERE id_campanha = %s
            {Bestiario._condicao_adicionada('bestiario')}
            ORDER BY nivel_revelacao DESC, nome
        """
        return Database.execute_query(query, (campanha_id,))

    @staticmethod
    def _condicao_adicionada(alias):
        """Criatura do acervo só entra na campanha se estiver marcada."""
        return f"""
            AND (
                NOT EXISTS (SELECT 1 FROM acervo_criaturas a WHERE a.nome = {alias}.nome)
                OR EXISTS (
                    SELECT 1 FROM acervo_criaturas a
                    INNER JOIN campanha_criatura cc
                        ON cc.id_acervo = a.id AND cc.id_campanha = {alias}.id_campanha
                    WHERE a.nome = {alias}.nome
                )
            )
        """

    @staticmethod
    def adicionada(criatura):
        if not criatura:
            return False
        consulta = Database.execute_query(
            f"SELECT id FROM bestiario WHERE id = %s {Bestiario._condicao_adicionada('bestiario')}",
            (criatura['id'],),
        )
        return bool(consulta)

    @staticmethod
    def buscar_por_id(criatura_id):
        result = Database.execute_query("SELECT * FROM bestiario WHERE id = %s", (criatura_id,))
        return result[0] if result else None

    @staticmethod
    def criar(dados):
        query = """
            INSERT INTO bestiario
            (id_campanha, nome, categoria, descricao_publica, descricao_mestre,
             imagem_url, ficha_personagem_id, nivel_revelacao)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            dados.get('id_campanha'),
            dados.get('nome'),
            dados.get('categoria'),
            dados.get('descricao_publica'),
            dados.get('descricao_mestre'),
            dados.get('imagem_url'),
            dados.get('ficha_personagem_id'),
            Bestiario.nivel_valido(dados.get('nivel_revelacao')),
        )
        return Database.execute_query(query, params, fetch=False)

    @staticmethod
    def atualizar(criatura_id, dados):
        query = f"""
            UPDATE bestiario SET {', '.join(f'{campo} = %s' for campo in _CAMPOS)}
            WHERE id = %s
        """
        params = tuple(dados.get(campo) for campo in _CAMPOS) + (criatura_id,)
        Database.execute_query(query, params, fetch=False)

    @staticmethod
    def definir_revelacao(criatura_id, nivel):
        Database.execute_query(
            "UPDATE bestiario SET nivel_revelacao = %s WHERE id = %s",
            (Bestiario.nivel_valido(nivel), criatura_id),
            fetch=False,
        )

    @staticmethod
    def deletar(criatura_id):
        Database.execute_query("DELETE FROM bestiario WHERE id = %s", (criatura_id,), fetch=False)

    @staticmethod
    def listar_imagens(criatura_id):
        return Database.execute_query(
            "SELECT * FROM bestiario_imagens WHERE id_bestiario = %s ORDER BY id",
            (criatura_id,),
        ) or []

    @staticmethod
    def adicionar_imagem(criatura_id, imagem_url):
        return Database.execute_query(
            "INSERT INTO bestiario_imagens (id_bestiario, imagem_url) VALUES (%s, %s)",
            (criatura_id, imagem_url),
            fetch=False,
        )

    @staticmethod
    def buscar_imagem(imagem_id):
        result = Database.execute_query("SELECT * FROM bestiario_imagens WHERE id = %s", (imagem_id,))
        return result[0] if result else None

    @staticmethod
    def deletar_imagem(imagem_id):
        Database.execute_query("DELETE FROM bestiario_imagens WHERE id = %s", (imagem_id,), fetch=False)

    @staticmethod
    def capas_por_ficha(campanha_id):
        """{ficha_personagem_id: imagem_url} das criaturas com capa."""
        result = Database.execute_query(
            """
            SELECT ficha_personagem_id, imagem_url FROM bestiario
            WHERE id_campanha = %s AND ficha_personagem_id IS NOT NULL AND imagem_url IS NOT NULL
        """ + Bestiario._condicao_adicionada('bestiario') + """
            """,
            (campanha_id,),
        )
        return {linha['ficha_personagem_id']: linha['imagem_url'] for linha in (result or [])}

    @staticmethod
    def fichas_bloqueadas(campanha_id):
        """IDs das fichas de criaturas que os jogadores ainda não derrotaram."""
        result = Database.execute_query(
            """
            SELECT ficha_personagem_id FROM bestiario
            WHERE id_campanha = %s AND nivel_revelacao < %s AND ficha_personagem_id IS NOT NULL
        """ + Bestiario._condicao_adicionada('bestiario') + """
            """,
            (campanha_id, Bestiario.DERROTADA),
        )
        return {linha['ficha_personagem_id'] for linha in (result or [])}
