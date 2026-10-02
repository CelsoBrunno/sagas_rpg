# ==========================================
# Catálogo de Perícias (GURPS)
# ==========================================

from database import Database


class PericiaCatalogo:
    @staticmethod
    def listar_todas():
        query = (
            """
            SELECT id, nome, atributo_base, dificuldade, custo_texto, descricao
            FROM pericias_catalogo
            ORDER BY nome
            """
        )
        return Database.execute_query(query)

    @staticmethod
    def buscar_por_id(pericia_id: int):
        query = "SELECT * FROM pericias_catalogo WHERE id = %s"
        result = Database.execute_query(query, (pericia_id,))
        return result[0] if result else None

    @staticmethod
    def criar_se_nao_existir(nome: str, atributo_base: str, dificuldade: str, custo_texto: str = None, descricao: str = None):
        query = (
            """
            INSERT INTO pericias_catalogo (nome, atributo_base, dificuldade, custo_texto, descricao)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                atributo_base = VALUES(atributo_base),
                dificuldade = VALUES(dificuldade),
                custo_texto = VALUES(custo_texto),
                descricao = VALUES(descricao)
            """
        )
        Database.execute_query(query, (nome, atributo_base, dificuldade, custo_texto, descricao), fetch=False)

    @staticmethod
    def criar(nome: str, atributo_base: str, dificuldade: str, custo_texto: str = None, descricao: str = None):
        """Cria uma nova perícia no catálogo"""
        query = """
            INSERT INTO pericias_catalogo (nome, atributo_base, dificuldade, custo_texto, descricao)
            VALUES (%s, %s, %s, %s, %s)
        """
        Database.execute_query(query, (nome, atributo_base, dificuldade, custo_texto, descricao), fetch=False)
        result = Database.execute_query("SELECT LAST_INSERT_ID() AS id")
        return result[0]['id'] if result else None

    @staticmethod
    def atualizar(pericia_id: int, nome: str = None, atributo_base: str = None, dificuldade: str = None, 
              custo_texto: str = None, descricao: str = None):
        """Atualiza uma perícia do catálogo"""
        updates = []
        params = []
        
        if nome is not None:
            updates.append("nome = %s")
            params.append(nome)
        if atributo_base is not None:
            updates.append("atributo_base = %s")
            params.append(atributo_base)
        if dificuldade is not None:
            updates.append("dificuldade = %s")
            params.append(dificuldade)
        if custo_texto is not None:
            updates.append("custo_texto = %s")
            params.append(custo_texto)
        if descricao is not None:
            updates.append("descricao = %s")
            params.append(descricao)
        
        if not updates:
            return False
        
        params.append(pericia_id)
        query = f"UPDATE pericias_catalogo SET {', '.join(updates)} WHERE id = %s"
        Database.execute_query(query, params, fetch=False)
        return True

    @staticmethod
    def deletar(pericia_id: int):
        """Remove uma perícia do catálogo"""
        query = "DELETE FROM pericias_catalogo WHERE id = %s"
        Database.execute_query(query, (pericia_id,), fetch=False)
        return True


