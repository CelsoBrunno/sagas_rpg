# ==========================================
# Módulo 3: Modelo de NPCs
# ==========================================

from database import Database

class NPC:
    """Modelo para a tabela de NPCs"""
    
    @staticmethod
    def criar(dados):
        """Cria um novo NPC"""
        query = """
            INSERT INTO npcs 
            (nome, status, descricao_breve, descricao_completa, imagem_url, local_atual_id, ficha_personagem_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            dados.get('nome'),
            dados.get('status', 'Vivo'),
            dados.get('descricao_breve'),
            dados.get('descricao_completa'),
            dados.get('imagem_url'),
            dados.get('local_atual_id'),
            dados.get('ficha_personagem_id')
        )
        return Database.execute_query(query, params, fetch=False)
    
    @staticmethod
    def listar_todos():
        """Lista todos os NPCs"""
        query = """
            SELECT npcs.*, 
                   locais.nome as local_nome,
                   personagens.nome as personagem_nome
            FROM npcs
            LEFT JOIN locais ON npcs.local_atual_id = locais.id
            LEFT JOIN personagens ON npcs.ficha_personagem_id = personagens.id
            ORDER BY npcs.nome
        """
        return Database.execute_query(query)
    
    @staticmethod
    def listar_por_local(local_id):
        """Lista NPCs presentes em um local específico"""
        query = """
            SELECT npcs.*, 
                   personagens.nome as personagem_nome
            FROM npcs
            LEFT JOIN personagens ON npcs.ficha_personagem_id = personagens.id
            WHERE npcs.local_atual_id = %s
            ORDER BY npcs.nome
        """
        return Database.execute_query(query, (local_id,))
    
    @staticmethod
    def listar_por_status(status):
        """Lista NPCs por status"""
        query = """
            SELECT npcs.*, 
                   locais.nome as local_nome
            FROM npcs
            LEFT JOIN locais ON npcs.local_atual_id = locais.id
            WHERE npcs.status = %s
            ORDER BY npcs.nome
        """
        return Database.execute_query(query, (status,))
    
    @staticmethod
    def buscar_por_id(npc_id):
        """Busca um NPC por ID"""
        query = """
            SELECT npcs.*, 
                   locais.nome as local_nome,
                   personagens.nome as personagem_nome
            FROM npcs
            LEFT JOIN locais ON npcs.local_atual_id = locais.id
            LEFT JOIN personagens ON npcs.ficha_personagem_id = personagens.id
            WHERE npcs.id = %s
        """
        result = Database.execute_query(query, (npc_id,))
        return result[0] if result else None
    
    @staticmethod
    def atualizar(npc_id, dados):
        """Atualiza um NPC"""
        query = """
            UPDATE npcs 
            SET nome = %s, status = %s, descricao_breve = %s, 
                descricao_completa = %s, imagem_url = %s, local_atual_id = %s, ficha_personagem_id = %s
            WHERE id = %s
        """
        params = (
            dados.get('nome'),
            dados.get('status'),
            dados.get('descricao_breve'),
            dados.get('descricao_completa'),
            dados.get('imagem_url'),
            dados.get('local_atual_id'),
            dados.get('ficha_personagem_id'),
            npc_id
        )
        Database.execute_query(query, params, fetch=False)
    
    @staticmethod
    def mover_para_local(npc_id, local_id):
        """Move um NPC para outro local"""
        query = "UPDATE npcs SET local_atual_id = %s WHERE id = %s"
        Database.execute_query(query, (local_id, npc_id), fetch=False)
    
    @staticmethod
    def deletar(npc_id):
        """Deleta um NPC"""
        query = "DELETE FROM npcs WHERE id = %s"
        Database.execute_query(query, (npc_id,), fetch=False)
    
    @staticmethod
    def buscar(termo):
        """Busca NPCs por termo"""
        query = """
            SELECT npcs.*, locais.nome as local_nome
            FROM npcs
            LEFT JOIN locais ON npcs.local_atual_id = locais.id
            WHERE npcs.nome LIKE %s OR npcs.descricao_breve LIKE %s
            ORDER BY npcs.nome
        """
        termo_like = f"%{termo}%"
        return Database.execute_query(query, (termo_like, termo_like))

