# ==========================================
# Módulo 6: Modelo de Imagens Polimórficas
# ==========================================

from database import Database

class Imagem:
    """Modelo para a tabela de imagens (Assets)"""
    
    @staticmethod
    def criar(dados):
        """Adiciona uma nova imagem"""
        query = """
            INSERT INTO imagens 
            (path_url, alt_text, titulo, descricao, entidade_tipo, entidade_id, 
             file_size, mime_type, width, height)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            dados.get('path_url'),
            dados.get('alt_text'),
            dados.get('titulo'),
            dados.get('descricao'),
            dados.get('entidade_tipo'),
            dados.get('entidade_id'),
            dados.get('file_size'),
            dados.get('mime_type'),
            dados.get('width'),
            dados.get('height')
        )
        return Database.execute_query(query, params, fetch=False)
    
    @staticmethod
    def buscar_por_entidade(entidade_tipo, entidade_id):
        """Busca todas as imagens de uma entidade"""
        query = """
            SELECT * FROM imagens 
            WHERE entidade_tipo = %s AND entidade_id = %s
            ORDER BY created_at ASC
        """
        return Database.execute_query(query, (entidade_tipo, entidade_id))
    
    @staticmethod
    def buscar_primeira(entidade_tipo, entidade_id):
        """Busca a primeira imagem de uma entidade (avatar/retrato)"""
        query = """
            SELECT * FROM imagens 
            WHERE entidade_tipo = %s AND entidade_id = %s
            ORDER BY created_at ASC
            LIMIT 1
        """
        result = Database.execute_query(query, (entidade_tipo, entidade_id))
        return result[0] if result else None
    
    @staticmethod
    def primeiras_por_entidades(entidade_tipo, entidade_ids):
        """Imagem mais recente de cada entidade, numa consulta só: {entidade_id: path_url}"""
        if not entidade_ids:
            return {}
        marcadores = ', '.join(['%s'] * len(entidade_ids))
        query = f"""
            SELECT entidade_id, path_url FROM imagens
            WHERE entidade_tipo = %s AND entidade_id IN ({marcadores})
            ORDER BY created_at, id
        """
        result = Database.execute_query(query, (entidade_tipo, *entidade_ids)) or []
        return {linha['entidade_id']: linha['path_url'] for linha in result}

    @staticmethod
    def buscar_todas_galeria(entidade_tipo, entidade_id):
        """Busca todas as imagens para galeria"""
        query = """
            SELECT * FROM imagens 
            WHERE entidade_tipo = %s AND entidade_id = %s
            ORDER BY created_at ASC
        """
        return Database.execute_query(query, (entidade_tipo, entidade_id))
    
    @staticmethod
    def buscar_por_id(imagem_id):
        """Busca uma imagem por ID"""
        query = "SELECT * FROM imagens WHERE id = %s"
        result = Database.execute_query(query, (imagem_id,))
        return result[0] if result else None
    
    @staticmethod
    def deletar(imagem_id):
        """Remove uma imagem"""
        query = "DELETE FROM imagens WHERE id = %s"
        Database.execute_query(query, (imagem_id,), fetch=False)
    
    @staticmethod
    def atualizar(imagem_id, dados):
        """Atualiza uma imagem"""
        query = """
            UPDATE imagens 
            SET alt_text = %s, titulo = %s, descricao = %s
            WHERE id = %s
        """
        params = (
            dados.get('alt_text'),
            dados.get('titulo'),
            dados.get('descricao'),
            imagem_id
        )
        Database.execute_query(query, params, fetch=False)

