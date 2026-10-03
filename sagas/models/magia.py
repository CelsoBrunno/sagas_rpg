# ==========================================
# Grimório: magias de cada personagem
# ==========================================

from database import Database

_CAMPOS = ('nome', 'escola', 'nh', 'custo', 'tempo', 'duracao', 'notas')


class Magia:
    # Escolas do GURPS 4e Módulo Básico (sugestões; o campo aceita outras)
    ESCOLAS = (
        'Água', 'Ar', 'Comunicação e Empatia', 'Conhecimento', 'Controle da Mente',
        'Controle do Corpo', 'Cura', 'Fogo', 'Luz e Trevas', 'Meta-Mágica',
        'Movimento', 'Necromancia', 'Portais', 'Proteção e Aviso', 'Terra',
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
