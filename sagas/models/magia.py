# ==========================================
# Grimório: magias de cada personagem
# ==========================================

from database import Database

_CAMPOS = ('nome', 'escola', 'nh', 'custo', 'tempo', 'duracao', 'notas')
_CAMPOS_CATALOGO = ('nome', 'escola', 'classe', 'dificuldade', 'custo', 'tempo', 'duracao',
                    'pre_requisitos', 'pagina', 'descricao')


class Magia:
    # Escolas do GURPS 4e Módulo Básico, com os nomes da edição em português
    ESCOLAS = (
        'Água', 'Ar', 'Comunicação e Empatia', 'Controle da Mente', 'Controle do Corpo',
        'Cura', 'Deslocamento', 'Fogo', 'Luz e Trevas', 'Metamágica',
        'Necromancia', 'Portal', 'Proteção e Aviso', 'Reconhecimento', 'Terra',
    )

    @staticmethod
    def listar_por_personagem(personagem_id):
        return Database.execute_query(
            "SELECT * FROM personagem_magias WHERE personagem_id = %s ORDER BY escola, nome",
            (personagem_id,),
        ) or []

    @staticmethod
    def buscar_por_id(magia_id):
        result = Database.execute_query("SELECT * FROM personagem_magias WHERE id = %s", (magia_id,))
        return result[0] if result else None

    @staticmethod
    def criar(personagem_id, dados):
        query = f"""
            INSERT INTO personagem_magias (personagem_id, {', '.join(_CAMPOS)})
            VALUES (%s, {', '.join(['%s'] * len(_CAMPOS))})
        """
        params = (personagem_id,) + tuple(dados.get(campo) for campo in _CAMPOS)
        return Database.execute_query(query, params, fetch=False)

    @staticmethod
    def atualizar(magia_id, dados):
        query = f"""
            UPDATE personagem_magias SET {', '.join(f'{campo} = %s' for campo in _CAMPOS)}
            WHERE id = %s
        """
        params = tuple(dados.get(campo) for campo in _CAMPOS) + (magia_id,)
        Database.execute_query(query, params, fetch=False)

    @staticmethod
    def deletar(magia_id):
        Database.execute_query("DELETE FROM personagem_magias WHERE id = %s", (magia_id,), fetch=False)


class MagiaCatalogo:
    @staticmethod
    def listar_todas():
        return Database.execute_query(
            "SELECT * FROM magias_catalogo WHERE origem = 'manual' ORDER BY escola, nome"
        ) or []

    @staticmethod
    def buscar_por_id(magia_id):
        result = Database.execute_query("SELECT * FROM magias_catalogo WHERE id = %s", (magia_id,))
        return result[0] if result else None

    @staticmethod
    def criar_ou_atualizar(dados):
        atualizacoes = ', '.join(f'{c} = VALUES({c})' for c in _CAMPOS_CATALOGO if c != 'nome')
        query = f"""
            INSERT INTO magias_catalogo ({', '.join(_CAMPOS_CATALOGO)})
            VALUES ({', '.join(['%s'] * len(_CAMPOS_CATALOGO))})
            ON DUPLICATE KEY UPDATE {atualizacoes}
        """
        Database.execute_query(query, tuple(dados.get(c) for c in _CAMPOS_CATALOGO), fetch=False)
