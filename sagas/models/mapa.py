# ==========================================
# Módulo 4: Modelo de Mapas
# ==========================================

from database import Database

class Mapa:
    """Modelo para a tabela de mapas"""
    
    @staticmethod
    def criar(dados):
        """Cria um novo mapa"""
        query = """
            INSERT INTO mapas 
            (nome_mapa, url_imagem, tipo_mapa, descricao, local_associado_id, id_campanha)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            dados.get('nome_mapa'),
            dados.get('url_imagem'),
            dados.get('tipo_mapa'),
            dados.get('descricao'),
            dados.get('local_associado_id'),
            dados.get('id_campanha')
        )
        return Database.execute_query(query, params, fetch=False)
    
    @staticmethod
    def listar_todos():
        """Lista todos os mapas"""
        query = """
            SELECT mapas.*, 
                   locais.nome as local_nome
            FROM mapas
            LEFT JOIN locais ON mapas.local_associado_id = locais.id
            ORDER BY mapas.nome_mapa
        """
        return Database.execute_query(query)
    
    @staticmethod
    def listar_por_campanha(campanha_id):
        """Lista os mapas de uma campanha"""
        query = """
            SELECT mapas.*, 
                   locais.nome as local_nome
            FROM mapas
            LEFT JOIN locais ON mapas.local_associado_id = locais.id
            WHERE mapas.id_campanha = %s
            ORDER BY mapas.nome_mapa
        """
        return Database.execute_query(query, (campanha_id,))
    
    @staticmethod
    def listar_por_local(local_id):
        """Lista mapas associados a um local específico"""
        query = """
            SELECT * FROM mapas 
            WHERE local_associado_id = %s
            ORDER BY nome_mapa
        """
        return Database.execute_query(query, (local_id,))
    
    @staticmethod
    def listar_por_tipo(tipo_mapa):
        """Lista mapas por tipo"""
        query = """
            SELECT mapas.*, locais.nome as local_nome
            FROM mapas
            LEFT JOIN locais ON mapas.local_associado_id = locais.id
            WHERE mapas.tipo_mapa = %s
            ORDER BY mapas.nome_mapa
        """
        return Database.execute_query(query, (tipo_mapa,))
    
    @staticmethod
    def listar_mapas_regionais():
        """Lista mapas regionais (sem local associado)"""
        query = """
            SELECT * FROM mapas 
            WHERE local_associado_id IS NULL
            ORDER BY nome_mapa
        """
        return Database.execute_query(query)
    
    @staticmethod
    def buscar_por_id(mapa_id):
        """Busca um mapa por ID"""
        query = """
            SELECT mapas.*, 
                   locais.nome as local_nome
            FROM mapas
            LEFT JOIN locais ON mapas.local_associado_id = locais.id
            WHERE mapas.id = %s
        """
        result = Database.execute_query(query, (mapa_id,))
        return result[0] if result else None
    
    @staticmethod
    def atualizar(mapa_id, dados):
        """Atualiza um mapa"""
        query = """
            UPDATE mapas 
            SET nome_mapa = %s, url_imagem = %s, tipo_mapa = %s, 
                descricao = %s, local_associado_id = %s
            WHERE id = %s
        """
        params = (
            dados.get('nome_mapa'),
            dados.get('url_imagem'),
            dados.get('tipo_mapa'),
            dados.get('descricao'),
            dados.get('local_associado_id'),
            mapa_id
        )
        Database.execute_query(query, params, fetch=False)
    
    @staticmethod
    def deletar(mapa_id):
        """Deleta um mapa"""
        query = "DELETE FROM mapas WHERE id = %s"
        Database.execute_query(query, (mapa_id,), fetch=False)
    
    @staticmethod
    def buscar(termo, campanha_id=None):
        """Busca mapas por termo, limitada à campanha quando informada"""
        query = """
            SELECT mapas.*, locais.nome as local_nome
            FROM mapas
            LEFT JOIN locais ON mapas.local_associado_id = locais.id
            WHERE (mapas.nome_mapa LIKE %s OR mapas.descricao LIKE %s)
        """
        termo_like = f"%{termo}%"
        params = [termo_like, termo_like]
        if campanha_id:
            query += " AND mapas.id_campanha = %s"
            params.append(campanha_id)
        query += " ORDER BY mapas.nome_mapa"
        return Database.execute_query(query, tuple(params))

