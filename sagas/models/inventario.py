# ==========================================
# Sistema de Campanha GURPS - Model: Inventario
# ==========================================

from database import Database

class Inventario:
    """Modelo para a tabela de inventário (itens por personagem)."""

    @staticmethod
    def criar(
        personagem_id: int,
        nome_item: str,
        quantidade: int = 1,
        peso: float = 0.0,
        notas: str = "",
        preco_unitario: float = 0.0,
        tipo_item: str = 'outro',
        dano_bal_mod: int | None = None,
        dano_bal_tipo: str | None = None,
        dano_gdp_mod: int | None = None,
        dano_gdp_tipo: str | None = None,
        rd_mod: int | None = None,
        rd_tipo: str | None = None
    ) -> int:
        tipo_item = (tipo_item or 'outro').lower()
        if tipo_item not in ('equipamento', 'consumivel', 'outro'):
            tipo_item = 'outro'
        dano_bal_mod = 0 if dano_bal_mod is None else int(dano_bal_mod)
        dano_gdp_mod = 0 if dano_gdp_mod is None else int(dano_gdp_mod)
        rd_mod = 0 if rd_mod is None else int(rd_mod)
        dano_bal_tipo = dano_bal_tipo or None
        dano_gdp_tipo = dano_gdp_tipo or None
        rd_tipo = rd_tipo or None
        query = (
            """
            INSERT INTO inventario (
                personagem_id, nome_item, quantidade, peso, preco_unitario, notas,
                quantidade_em_uso, tipo_item,
                dano_bal_mod, dano_bal_tipo, dano_gdp_mod, dano_gdp_tipo,
                rd_mod, rd_tipo
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        )
        params = (
            personagem_id, nome_item, quantidade, peso, preco_unitario, notas,
            0, tipo_item,
            dano_bal_mod, dano_bal_tipo, dano_gdp_mod, dano_gdp_tipo,
            rd_mod, rd_tipo
        )
        return Database.execute_query(query, params, fetch=False)

    @staticmethod
    def listar_por_personagem(personagem_id: int):
        query = (
            """
            SELECT i.id,
                   i.personagem_id,
                   i.nome_item,
                   i.quantidade,
                   i.peso,
                   i.notas,
                   COALESCE(i.quantidade_em_uso, 0) AS quantidade_em_uso,
                   COALESCE(i.preco_unitario, 0) AS preco_unitario,
                   i.tipo_item,
                   COALESCE(i.dano_bal_mod, 0) AS dano_bal_mod,
                   i.dano_bal_tipo,
                   COALESCE(i.dano_gdp_mod, 0) AS dano_gdp_mod,
                   i.dano_gdp_tipo,
                   COALESCE(i.rd_mod, 0) AS rd_mod,
                   i.rd_tipo,
                   ep.slot AS slot_equipado
            FROM inventario i
            LEFT JOIN equipamentos_personagem ep ON ep.inventario_id = i.id
            WHERE i.personagem_id = %s
            ORDER BY i.nome_item
            """
        )
        return Database.execute_query(query, (personagem_id,))

    @staticmethod
    def buscar_por_id(item_id: int):
        query = (
            """
            SELECT i.id,
                   i.personagem_id,
                   i.nome_item,
                   i.quantidade,
                   i.peso,
                   i.notas,
                   COALESCE(i.quantidade_em_uso, 0) AS quantidade_em_uso,
                   COALESCE(i.preco_unitario, 0) AS preco_unitario,
                   i.tipo_item,
                   COALESCE(i.dano_bal_mod, 0) AS dano_bal_mod,
                   i.dano_bal_tipo,
                   COALESCE(i.dano_gdp_mod, 0) AS dano_gdp_mod,
                   i.dano_gdp_tipo,
                   COALESCE(i.rd_mod, 0) AS rd_mod,
                   i.rd_tipo
            FROM inventario i
            WHERE i.id = %s
            """
        )
        resultado = Database.execute_query(query, (item_id,))
        return resultado[0] if resultado else None

    @staticmethod
    def deletar(item_id: int) -> None:
        query = "DELETE FROM inventario WHERE id = %s"
        Database.execute_query(query, (item_id,), fetch=False)

    @staticmethod
    def atualizar(item_id: int, quantidade: int, peso: float, notas: str = "", preco_unitario: float = None) -> None:
        campos = ["quantidade = %s", "peso = %s", "notas = %s"]
        valores = [quantidade, peso, notas]

        if preco_unitario is not None:
            campos.append("preco_unitario = %s")
            valores.append(preco_unitario)

        set_clause = ", ".join(campos)
        query = (
            """
            UPDATE inventario
            SET {set_clause}
            WHERE id = %s
            """
        ).format(set_clause=set_clause)
        valores.append(item_id)
        Database.execute_query(query, tuple(valores), fetch=False)

    @staticmethod
    def atualizar_em_uso(item_id: int, quantidade_em_uso: int) -> None:
        query = (
            """
            UPDATE inventario
            SET quantidade_em_uso = %s
            WHERE id = %s
            """
        )
        Database.execute_query(query, (quantidade_em_uso, item_id), fetch=False)

    @staticmethod
    def consumir(item_id: int, quantidade: int = 1) -> None:
        """Decrementa a quantidade do item sem deixar negativo."""
        query = (
            """
            UPDATE inventario
            SET quantidade = CASE WHEN quantidade - %s < 0 THEN 0 ELSE quantidade - %s END
            WHERE id = %s
            """
        )
        Database.execute_query(query, (quantidade, quantidade, item_id), fetch=False)

    @staticmethod
    def calcular_peso_total(personagem_id: int) -> float:
        itens = Inventario.listar_por_personagem(personagem_id)
        return float(sum((item.get("peso") or 0) * (item.get("quantidade") or 0) for item in itens))

    @staticmethod
    def calcular_valor_total(personagem_id: int) -> float:
        itens = Inventario.listar_por_personagem(personagem_id)
        return float(sum((item.get("preco_unitario") or 0) * (item.get("quantidade") or 0) for item in itens))
