from typing import List, Optional

from database import Database


class Equipamento:
    """Modelo responsável pelos slots de equipamento de um personagem."""

    SLOTS_VALIDOS = {'mao_direita', 'mao_esquerda', 'armadura', 'vestimenta', 'acessorio'}

    @staticmethod
    def listar_por_personagem(personagem_id: int):
        query = """
            SELECT id, personagem_id, inventario_id, slot, created_at
            FROM equipamentos_personagem
            WHERE personagem_id = %s
            ORDER BY FIELD(slot, 'mao_direita', 'mao_esquerda', 'armadura', 'vestimenta', 'acessorio'), created_at
        """
        return Database.execute_query(query, (personagem_id,))

    @staticmethod
    def buscar_por_item(inventario_id: int) -> Optional[dict]:
        query = """
            SELECT id, personagem_id, inventario_id, slot, created_at
            FROM equipamentos_personagem
            WHERE inventario_id = %s
        """
        resultado = Database.execute_query(query, (inventario_id,))
        return resultado[0] if resultado else None

    @staticmethod
    def equipar(personagem_id: int, inventario_id: int, slot: str) -> None:
        if slot not in Equipamento.SLOTS_VALIDOS:
            raise ValueError('Slot inválido')

        Database.execute_query(
            "DELETE FROM equipamentos_personagem WHERE inventario_id = %s",
            (inventario_id,),
            fetch=False
        )

        if slot != 'acessorio':
            Database.execute_query(
                "DELETE FROM equipamentos_personagem WHERE personagem_id = %s AND slot = %s",
                (personagem_id, slot),
                fetch=False
            )

        Database.execute_query(
            """
            INSERT INTO equipamentos_personagem (personagem_id, inventario_id, slot)
            VALUES (%s, %s, %s)
            """,
            (personagem_id, inventario_id, slot),
            fetch=False
        )

    @staticmethod
    def desequipar(inventario_id: int) -> None:
        Database.execute_query(
            "DELETE FROM equipamentos_personagem WHERE inventario_id = %s",
            (inventario_id,),
            fetch=False
        )

    @staticmethod
    def slots_ocupados(personagem_id: int) -> List[dict]:
        return Equipamento.listar_por_personagem(personagem_id)
