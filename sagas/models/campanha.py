# ==========================================
# Modelo de Campanhas
# ==========================================

from database import Database

class Campanha:
    # Cada tema diferente de 'padrao' precisa de static/css/tema-<chave>.css
    TEMAS = {
        'padrao': 'Padrão (SagaS)',
        'myth': 'Myth (sombrio)',
    }

    @staticmethod
    def criar(dados):
        """Cria uma nova campanha"""
        query = """
            INSERT INTO campanhas 
            (nome_campanha, id_mestre, pontos_iniciais, descricao, status)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            dados.get('nome_campanha'),
            dados.get('id_mestre'),
            dados.get('pontos_iniciais', 100),
            dados.get('descricao'),
            dados.get('status', 'Ativa')
        )
        return Database.execute_query(query, params, fetch=False)
    
    @staticmethod
    def listar_por_mestre(id_mestre):
        """Lista campanhas do mestre"""
        query = """
            SELECT c.*, 
                   COUNT(p.id) as total_personagens
            FROM campanhas c
            LEFT JOIN personagens p ON c.id = p.id_campanha
            WHERE c.id_mestre = %s
            GROUP BY c.id
            ORDER BY c.created_at DESC
        """
        return Database.execute_query(query, (id_mestre,))
    
    @staticmethod
    def buscar_por_id(campanha_id):
        """Busca uma campanha por ID"""
        query = "SELECT * FROM campanhas WHERE id = %s"
        result = Database.execute_query(query, (campanha_id,))
        return result[0] if result else None
    
    @staticmethod
    def atualizar(campanha_id, dados):
        """Atualiza uma campanha"""
        query = """
            UPDATE campanhas 
            SET nome_campanha = %s, pontos_iniciais = %s, 
                descricao = %s, status = %s, tema = %s
            WHERE id = %s
        """
        params = (
            dados.get('nome_campanha'),
            dados.get('pontos_iniciais'),
            dados.get('descricao'),
            dados.get('status'),
            dados.get('tema', 'padrao'),
            campanha_id
        )
        Database.execute_query(query, params, fetch=False)
    
    @staticmethod
    def convidar_jogador(campanha_id, usuario_id):
        """Convide um jogador para a campanha (cria personagem pendente)"""
        query = """
            INSERT INTO personagens 
            (nome, id_campanha, id_usuario_jogador, status_criacao, tipo)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            f"Personagem do Usuário {usuario_id}",
            campanha_id,
            usuario_id,
            'Pendente',
            'PJ'
        )
        return Database.execute_query(query, params, fetch=False)

    @staticmethod
    def listar_todas():
        """Lista todas as campanhas"""
        query = """
            SELECT c.*, 
                   u.username AS mestre_username,
                   COUNT(p.id) as total_personagens
            FROM campanhas c
            LEFT JOIN usuarios u ON c.id_mestre = u.id
            LEFT JOIN personagens p ON c.id = p.id_campanha
            GROUP BY c.id
            ORDER BY c.created_at DESC
        """
        return Database.execute_query(query)

