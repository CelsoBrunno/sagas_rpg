# ==========================================
# Módulo 7: Sessões e Distribuição de Pontos
# ==========================================

from typing import List, Dict
from database import Database


class SessaoLog:
    @staticmethod
    def criar_transacional(data_sessao: str, descricao: str, distribuicoes: List[Dict]):
        """
        Cria uma sessão e distribui pontos para PCs em uma transação atômica.
        distribuicoes: lista de dicts { 'personagem_id': int, 'pontos': int }
        """
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            cursor = connection.cursor(dictionary=True)

            # 1) Inserir sessão
            cursor.execute(
                """
                INSERT INTO sessoes_log (data_sessao, descricao)
                VALUES (%s, %s)
                """,
                (data_sessao, descricao)
            )
            sessao_id = cursor.lastrowid

            # 2) Para cada distribuição, inserir recibo e atualizar personagem
            for item in distribuicoes:
                personagem_id = int(item['personagem_id'])
                pontos = int(item['pontos'])
                if pontos == 0:
                    continue

                cursor.execute(
                    """
                    INSERT INTO sessoes_pontos_pc (sessao_id, personagem_id, pontos_ganhos)
                    VALUES (%s, %s, %s)
                    """,
                    (sessao_id, personagem_id, pontos)
                )

                cursor.execute(
                    """
                    UPDATE personagens
                    SET pontos_ganhos = pontos_ganhos + %s
                    WHERE id = %s
                    """,
                    (pontos, personagem_id)
                )

            connection.commit()
            return sessao_id

        except Exception:
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    @staticmethod
    def listar_historico_sessoes():
        """Lista sessões com seus recebimentos agrupados."""
        query = (
            """
            SELECT s.id, s.data_sessao, s.descricao,
                   sp.personagem_id, p.nome AS personagem_nome, sp.pontos_ganhos
            FROM sessoes_log s
            LEFT JOIN sessoes_pontos_pc sp ON sp.sessao_id = s.id
            LEFT JOIN personagens p ON p.id = sp.personagem_id
            ORDER BY s.data_sessao DESC, p.nome ASC
            """
        )
        return Database.execute_query(query)

    @staticmethod
    def listar_historico_por_personagem(personagem_id: int):
        query = (
            """
            SELECT s.data_sessao, s.descricao, sp.pontos_ganhos
            FROM sessoes_pontos_pc sp
            JOIN sessoes_log s ON s.id = sp.sessao_id
            WHERE sp.personagem_id = %s
            ORDER BY s.data_sessao DESC
            """
        )
        return Database.execute_query(query, (personagem_id,))


