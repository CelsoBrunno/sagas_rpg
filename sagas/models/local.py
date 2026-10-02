# ==========================================
# Módulo 2: Modelo de Locais
# ==========================================

from database import Database

class Local:
    """Modelo para a tabela de locais (O Hub Central)"""
    
    @staticmethod
    def criar(dados):
        """Cria um novo local"""
        query = """
            INSERT INTO locais 
            (nome, tipo, descricao_publica, descricao_mestre, imagem_principal_url)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            dados.get('nome'),
            dados.get('tipo'),
            dados.get('descricao_publica'),
            dados.get('descricao_mestre'),
            dados.get('imagem_principal_url')
        )
        return Database.execute_query(query, params, fetch=False)
    
    @staticmethod
    def listar_todos():
        """Lista todos os locais"""
        query = "SELECT * FROM locais ORDER BY nome"
        return Database.execute_query(query)
    
    @staticmethod
    def listar_por_tipo(tipo):
        """Lista locais por tipo"""
        query = "SELECT * FROM locais WHERE tipo = %s ORDER BY nome"
        return Database.execute_query(query, (tipo,))
    
    @staticmethod
    def buscar_por_id(local_id):
        """Busca um local por ID"""
        query = "SELECT * FROM locais WHERE id = %s"
        result = Database.execute_query(query, (local_id,))
        return result[0] if result else None
    
    @staticmethod
    def atualizar(local_id, dados):
        """Atualiza um local"""
        query = """
            UPDATE locais 
            SET nome = %s, tipo = %s, descricao_publica = %s, 
                descricao_mestre = %s, imagem_principal_url = %s
            WHERE id = %s
        """
        params = (
            dados.get('nome'),
            dados.get('tipo'),
            dados.get('descricao_publica'),
            dados.get('descricao_mestre'),
            dados.get('imagem_principal_url'),
            local_id
        )
        Database.execute_query(query, params, fetch=False)
    
    @staticmethod
    def deletar(local_id):
        """Deleta um local"""
        query = "DELETE FROM locais WHERE id = %s"
        Database.execute_query(query, (local_id,), fetch=False)
    
    @staticmethod
    def buscar(termo):
        """Busca locais por termo"""
        query = """
            SELECT * FROM locais 
            WHERE nome LIKE %s OR descricao_publica LIKE %s 
            ORDER BY nome
        """
        termo_like = f"%{termo}%"
        return Database.execute_query(query, (termo_like, termo_like))

