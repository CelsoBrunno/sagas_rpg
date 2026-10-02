# ==========================================
# Catálogo de Vantagens e Desvantagens (GURPS)
# ==========================================

from database import Database


class VantagemDesvantagemCatalogo:
    @staticmethod
    def listar_todas():
        """Lista todas as vantagens e desvantagens do catálogo"""
        query = """
            SELECT id, nome, tipo, custo_base, custo_texto, descricao, categoria
            FROM vantagens_desvantagens_catalogo
            ORDER BY tipo DESC, nome
        """
        return Database.execute_query(query)
    
    @staticmethod
    def listar_vantagens():
        """Lista apenas vantagens"""
        query = """
            SELECT id, nome, tipo, custo_base, custo_texto, descricao, categoria
            FROM vantagens_desvantagens_catalogo
            WHERE tipo = 'Vantagem'
            ORDER BY nome
        """
        return Database.execute_query(query)
    
    @staticmethod
    def listar_desvantagens():
        """Lista apenas desvantagens"""
        query = """
            SELECT id, nome, tipo, custo_base, custo_texto, descricao, categoria
            FROM vantagens_desvantagens_catalogo
            WHERE tipo = 'Desvantagem'
            ORDER BY nome
        """
        return Database.execute_query(query)
    
    @staticmethod
    def buscar_por_id(vd_id: int):
        """Busca uma vantagem/desvantagem por ID"""
        query = "SELECT * FROM vantagens_desvantagens_catalogo WHERE id = %s"
        result = Database.execute_query(query, (vd_id,))
        return result[0] if result else None
    
    @staticmethod
    def buscar_por_nome(nome: str):
        """Busca uma vantagem/desvantagem por nome"""
        query = "SELECT * FROM vantagens_desvantagens_catalogo WHERE nome LIKE %s"
        result = Database.execute_query(query, (f'%{nome}%',))
        return result
    
    @staticmethod
    def criar_se_nao_existir(nome: str, tipo: str, custo_base: int, custo_texto: str = None, descricao: str = None, categoria: str = None):
        """Cria uma entrada no catálogo se não existir"""
        query = """
            INSERT INTO vantagens_desvantagens_catalogo (nome, tipo, custo_base, custo_texto, descricao, categoria)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                tipo = VALUES(tipo),
                custo_base = VALUES(custo_base),
                custo_texto = VALUES(custo_texto),
                descricao = VALUES(descricao),
                categoria = VALUES(categoria)
        """
        Database.execute_query(query, (nome, tipo, custo_base, custo_texto, descricao, categoria), fetch=False)

    @staticmethod
    def criar(nome: str, tipo: str, custo_base: int, custo_texto: str = None, descricao: str = None, categoria: str = None):
        """Cria uma nova vantagem/desvantagem no catálogo"""
        query = """
            INSERT INTO vantagens_desvantagens_catalogo (nome, tipo, custo_base, custo_texto, descricao, categoria)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        Database.execute_query(query, (nome, tipo, custo_base, custo_texto, descricao, categoria), fetch=False)
        result = Database.execute_query("SELECT LAST_INSERT_ID() AS id")
        return result[0]['id'] if result else None

    @staticmethod
    def atualizar(vd_id: int, nome: str = None, tipo: str = None, custo_base: int = None, 
              custo_texto: str = None, descricao: str = None, categoria: str = None):
        """Atualiza uma vantagem/desvantagem do catálogo"""
        updates = []
        params = []
        
        if nome is not None:
            updates.append("nome = %s")
            params.append(nome)
        if tipo is not None:
            updates.append("tipo = %s")
            params.append(tipo)
        if custo_base is not None:
            updates.append("custo_base = %s")
            params.append(int(custo_base))
        if custo_texto is not None:
            updates.append("custo_texto = %s")
            params.append(custo_texto)
        if descricao is not None:
            updates.append("descricao = %s")
            params.append(descricao)
        if categoria is not None:
            updates.append("categoria = %s")
            params.append(categoria)
        
        if not updates:
            return False
        
        params.append(vd_id)
        query = f"UPDATE vantagens_desvantagens_catalogo SET {', '.join(updates)} WHERE id = %s"
        Database.execute_query(query, params, fetch=False)
        return True

    @staticmethod
    def deletar(vd_id: int):
        """Remove uma vantagem/desvantagem do catálogo"""
        query = "DELETE FROM vantagens_desvantagens_catalogo WHERE id = %s"
        Database.execute_query(query, (vd_id,), fetch=False)
        return True

