# ==========================================
# Catálogo de Itens (GURPS)
# ==========================================

from __future__ import annotations

from database import Database


class ItemCatalogo:
    """Modelo para manipulação do catálogo de itens."""

    @staticmethod
    def listar_todos():
        query = """
            SELECT id, nome, categoria, preco, peso, descricao, tipo_item,
                   COALESCE(dano_bal_mod, 0) AS dano_bal_mod,
                   dano_bal_tipo,
                   COALESCE(dano_gdp_mod, 0) AS dano_gdp_mod,
                   dano_gdp_tipo,
                   COALESCE(rd_mod, 0) AS rd_mod,
                   rd_tipo
            FROM itens_catalogo
            ORDER BY nome
        """
        return Database.execute_query(query)

    @staticmethod
    def buscar_por_id(item_id: int):
        query = "SELECT * FROM itens_catalogo WHERE id = %s"
        result = Database.execute_query(query, (item_id,))
        return result[0] if result else None

    @staticmethod
    def criar_se_nao_existir(
        nome: str,
        categoria: str,
        preco: float,
        peso: float = 0.0,
        descricao: str = None,
        tipo_item: str = 'outro',
        dano_bal_mod: int | None = None,
        dano_bal_tipo: str | None = None,
        dano_gdp_mod: int | None = None,
        dano_gdp_tipo: str | None = None,
        rd_mod: int | None = None,
        rd_tipo: str | None = None
    ):
        tipo_item = (tipo_item or 'outro').lower()
        if tipo_item not in ('equipamento', 'consumivel', 'outro'):
            tipo_item = 'outro'
        dano_bal_mod = 0 if dano_bal_mod is None else int(dano_bal_mod)
        dano_gdp_mod = 0 if dano_gdp_mod is None else int(dano_gdp_mod)
        rd_mod = 0 if rd_mod is None else int(rd_mod)
        dano_bal_tipo = (dano_bal_tipo or None)
        dano_gdp_tipo = (dano_gdp_tipo or None)
        rd_tipo = (rd_tipo or None)
        query = """
            INSERT INTO itens_catalogo (nome, categoria, preco, peso, descricao, tipo_item,
                                        dano_bal_mod, dano_bal_tipo, dano_gdp_mod, dano_gdp_tipo,
                                        rd_mod, rd_tipo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                categoria = VALUES(categoria),
                preco = VALUES(preco),
                peso = VALUES(peso),
                descricao = VALUES(descricao),
                tipo_item = VALUES(tipo_item),
                dano_bal_mod = VALUES(dano_bal_mod),
                dano_bal_tipo = VALUES(dano_bal_tipo),
                dano_gdp_mod = VALUES(dano_gdp_mod),
                dano_gdp_tipo = VALUES(dano_gdp_tipo),
                rd_mod = VALUES(rd_mod),
                rd_tipo = VALUES(rd_tipo)
        """
        params = (
            nome, categoria, preco, peso, descricao, tipo_item,
            dano_bal_mod, dano_bal_tipo, dano_gdp_mod, dano_gdp_tipo,
            rd_mod, rd_tipo
        )
        Database.execute_query(query, params, fetch=False)

    @staticmethod
    def criar(
        nome: str,
        categoria: str,
        preco: float,
        peso: float = 0.0,
        descricao: str = None,
        tipo_item: str = 'outro',
        dano_bal_mod: int | None = None,
        dano_bal_tipo: str | None = None,
        dano_gdp_mod: int | None = None,
        dano_gdp_tipo: str | None = None,
        rd_mod: int | None = None,
        rd_tipo: str | None = None
    ):
        """Cria um novo item no catálogo"""
        tipo_item = (tipo_item or 'outro').lower()
        if tipo_item not in ('equipamento', 'consumivel', 'outro'):
            tipo_item = 'outro'
        dano_bal_mod = 0 if dano_bal_mod is None else int(dano_bal_mod)
        dano_gdp_mod = 0 if dano_gdp_mod is None else int(dano_gdp_mod)
        rd_mod = 0 if rd_mod is None else int(rd_mod)
        
        query = """
            INSERT INTO itens_catalogo 
            (nome, categoria, preco, peso, descricao, tipo_item,
             dano_bal_mod, dano_bal_tipo, dano_gdp_mod, dano_gdp_tipo,
             rd_mod, rd_tipo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            nome, categoria, preco, peso, descricao, tipo_item,
            dano_bal_mod, dano_bal_tipo, dano_gdp_mod, dano_gdp_tipo,
            rd_mod, rd_tipo
        )
        Database.execute_query(query, params, fetch=False)
        result = Database.execute_query("SELECT LAST_INSERT_ID() AS id")
        return result[0]['id'] if result else None

    @staticmethod
    def atualizar(
        item_id: int,
        nome: str = None,
        categoria: str = None,
        preco: float = None,
        peso: float = None,
        descricao: str = None,
        tipo_item: str = None,
        dano_bal_mod: int | None = None,
        dano_bal_tipo: str | None = None,
        dano_gdp_mod: int | None = None,
        dano_gdp_tipo: str | None = None,
        rd_mod: int | None = None,
        rd_tipo: str | None = None
    ):
        """Atualiza um item do catálogo"""
        updates = []
        params = []
        
        if nome is not None:
            updates.append("nome = %s")
            params.append(nome)
        if categoria is not None:
            updates.append("categoria = %s")
            params.append(categoria)
        if preco is not None:
            updates.append("preco = %s")
            params.append(float(preco))
        if peso is not None:
            updates.append("peso = %s")
            params.append(float(peso))
        if descricao is not None:
            updates.append("descricao = %s")
            params.append(descricao)
        if tipo_item is not None:
            tipo_item = tipo_item.lower()
            if tipo_item in ('equipamento', 'consumivel', 'outro'):
                updates.append("tipo_item = %s")
                params.append(tipo_item)
        if dano_bal_mod is not None:
            updates.append("dano_bal_mod = %s")
            params.append(int(dano_bal_mod))
        if dano_bal_tipo is not None:
            updates.append("dano_bal_tipo = %s")
            params.append(dano_bal_tipo)
        if dano_gdp_mod is not None:
            updates.append("dano_gdp_mod = %s")
            params.append(int(dano_gdp_mod))
        if dano_gdp_tipo is not None:
            updates.append("dano_gdp_tipo = %s")
            params.append(dano_gdp_tipo)
        if rd_mod is not None:
            updates.append("rd_mod = %s")
            params.append(int(rd_mod))
        if rd_tipo is not None:
            updates.append("rd_tipo = %s")
            params.append(rd_tipo)
        
        if not updates:
            return False
        
        params.append(item_id)
        query = f"UPDATE itens_catalogo SET {', '.join(updates)} WHERE id = %s"
        Database.execute_query(query, params, fetch=False)
        return True

    @staticmethod
    def deletar(item_id: int):
        """Remove um item do catálogo"""
        query = "DELETE FROM itens_catalogo WHERE id = %s"
        Database.execute_query(query, (item_id,), fetch=False)
        return True

