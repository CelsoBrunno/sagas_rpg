# ==========================================
# Sistema de Campanha GURPS - Modelos
# ==========================================

from database import Database
from models.atributos import Atributos

class Personagem:
    """Modelo para a tabela de personagens"""
    
    @staticmethod
    def criar(dados):
        """Cria um novo personagem"""
        query = """
            INSERT INTO personagens 
            (nome, jogador_nome, raca, categoria, pontos_base, pontos_desvantagens_max, biografia, tipo, status, id_usuario_jogador, raca_id, classe_id, id_campanha)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            dados.get('nome'),
            dados.get('jogador_nome'),
            dados.get('raca'),
            dados.get('categoria', 'Humano'),
            dados.get('pontos_base', 0),
            dados.get('pontos_desvantagens_max', 0),
            dados.get('biografia'),
            dados.get('tipo', 'PJ'),
            dados.get('status', 'Ativo'),
            dados.get('id_usuario_jogador'),
            dados.get('raca_id'),
            dados.get('classe_id'),
            dados.get('id_campanha')
        )
        return Database.execute_query(query, params, fetch=False)
    
    @staticmethod
    def listar_todos():
        """Lista todos os personagens com informações do jogador associado (se houver)."""
        query = """
            SELECT p.*,
                   u.username AS usuario_username,
                   u.nome_completo AS usuario_nome_completo
            FROM personagens p
            LEFT JOIN usuarios u ON u.id = p.id_usuario_jogador
            ORDER BY p.nome
        """
        return Database.execute_query(query)
    
    @staticmethod
    def listar_por_campanha(campanha_id):
        """Lista os personagens de uma campanha."""
        query = """
            SELECT p.*,
                   u.username AS usuario_username,
                   u.nome_completo AS usuario_nome_completo
            FROM personagens p
            LEFT JOIN usuarios u ON u.id = p.id_usuario_jogador
            WHERE p.id_campanha = %s
            ORDER BY p.nome
        """
        return Database.execute_query(query, (campanha_id,))
    
    @staticmethod
    def buscar_por_id(personagem_id):
        """Busca um personagem por ID com dados do jogador vinculado."""
        query = """
            SELECT p.*,
                   u.username AS usuario_username,
                   u.nome_completo AS usuario_nome_completo
            FROM personagens p
            LEFT JOIN usuarios u ON u.id = p.id_usuario_jogador
            WHERE p.id = %s
        """
        result = Database.execute_query(query, (personagem_id,))
        return result[0] if result else None
    
    @staticmethod
    def buscar_por_usuario(usuario_id):
        """Busca o personagem de um usuário (cada usuário pode ter apenas um)"""
        query = """
            SELECT p.*,
                   u.username AS usuario_username,
                   u.nome_completo AS usuario_nome_completo
            FROM personagens p
            LEFT JOIN usuarios u ON u.id = p.id_usuario_jogador
            WHERE p.id_usuario_jogador = %s AND p.tipo = 'PJ'
            ORDER BY p.created_at DESC
            LIMIT 1
        """
        result = Database.execute_query(query, (usuario_id,))
        return result[0] if result else None

    @staticmethod
    def listar_por_usuario(usuario_id, campanha_id):
        """Fichas de jogador do usuário na campanha: as que ele criou e as que o mestre atribuiu."""
        query = """
            SELECT id, nome, raca, pontos_base, pontos_gastos
            FROM personagens
            WHERE id_usuario_jogador = %s AND tipo = 'PJ' AND id_campanha = %s
            ORDER BY nome
        """
        return Database.execute_query(query, (usuario_id, campanha_id)) or []

    @staticmethod
    def definir_dono(personagem_id, usuario_id):
        """Com dono, a ficha vira PJ do usuário; sem dono (None), volta a ser NPC."""
        tem_dono = usuario_id is not None
        Database.execute_query(
            "UPDATE personagens SET id_usuario_jogador = %s, tipo = %s, is_pc = %s WHERE id = %s",
            (usuario_id, 'PJ' if tem_dono else 'NPC', tem_dono, personagem_id),
            fetch=False,
        )
    
    @staticmethod
    def atualizar(personagem_id, dados):
        """Atualiza um personagem"""
        query = """
            UPDATE personagens 
            SET nome = %s, jogador_nome = %s, raca = %s, categoria = %s, pontos_base = %s,
                pontos_desvantagens_max = %s, biografia = %s, status = %s
            WHERE id = %s
        """
        params = (
            dados.get('nome'),
            dados.get('jogador_nome'),
            dados.get('raca'),
            dados.get('categoria', 'Humano'),
            dados.get('pontos_base'),
            dados.get('pontos_desvantagens_max'),
            dados.get('biografia'),
            dados.get('status'),
            personagem_id
        )
        Database.execute_query(query, params, fetch=False)
    
    @staticmethod
    def deletar(personagem_id):
        """Deleta um personagem"""
        query = "DELETE FROM personagens WHERE id = %s"
        Database.execute_query(query, (personagem_id,), fetch=False)
    
    @staticmethod
    def recalcular_pontos_gastos(personagem_id):
        """Recalcula e atualiza os pontos gastos do personagem"""
        # Busca atributos
        atributos = Atributos.buscar_por_personagem(personagem_id)
        if atributos:
            # Recalcula custo incluindo todos os extras
            custo_atributos = Atributos._calcular_custo_atributos(
                atributos['ST'], 
                atributos['DX'], 
                atributos['IQ'], 
                atributos['HT'],
                atributos.get('PV_extra', 0) or 0,
                atributos.get('PF_extra', 0) or 0,
                atributos.get('percepcao_extra', 0) or 0,
                atributos.get('vontade_extra', 0) or 0
            )
            # Atualiza o custo no banco
            Database.execute_query(
                "UPDATE atributos SET custo_total_atributos = %s WHERE personagem_id = %s",
                (custo_atributos, personagem_id),
                fetch=False
            )
        else:
            custo_atributos = 0
        
        # Soma vantagens/desvantagens
        query_vd = """
            SELECT SUM(custo_em_pontos) as total 
            FROM vantagens_desvantagens 
            WHERE personagem_id = %s
        """
        result_vd = Database.execute_query(query_vd, (personagem_id,))
        custo_vd = int(result_vd[0]['total'] or 0) if result_vd else 0
        
        # Soma perícias (pontos investidos)
        query_per = """
            SELECT SUM(pontos_investidos) as total 
            FROM pericias 
            WHERE personagem_id = %s
        """
        result_per = Database.execute_query(query_per, (personagem_id,))
        custo_pericias = int(result_per[0]['total'] or 0) if result_per else 0
        
        # Total gasto
        pontos_gastos = custo_atributos + custo_vd + custo_pericias
        
        # Atualiza no personagem
        query_update = "UPDATE personagens SET pontos_gastos = %s WHERE id = %s"
        Database.execute_query(query_update, (pontos_gastos, personagem_id), fetch=False)
        
        return pontos_gastos

    @staticmethod
    def atualizar_dinheiro(personagem_id, novo_valor):
        query = "UPDATE personagens SET dinheiro = %s WHERE id = %s"
        Database.execute_query(query, (novo_valor, personagem_id), fetch=False)

    @staticmethod
    def listar_por_status_criacao(status_criacao):
        """Lista personagens por status de criação"""
        query = """
            SELECT p.*,
                   u.username AS usuario_username,
                   u.nome_completo AS usuario_nome_completo,
                   c.nome_campanha
            FROM personagens p
            LEFT JOIN usuarios u ON u.id = p.id_usuario_jogador
            LEFT JOIN campanhas c ON c.id = p.id_campanha
            WHERE p.status_criacao = %s
            ORDER BY p.created_at DESC
        """
        return Database.execute_query(query, (status_criacao,))

    @staticmethod
    def atualizar_status_criacao(personagem_id, novo_status, observacoes_mestre=None):
        """Atualiza o status de criação de um personagem"""
        if observacoes_mestre is not None:
            query = "UPDATE personagens SET status_criacao = %s, observacoes_mestre = %s WHERE id = %s"
            Database.execute_query(query, (novo_status, observacoes_mestre, personagem_id), fetch=False)
        else:
            query = "UPDATE personagens SET status_criacao = %s WHERE id = %s"
            Database.execute_query(query, (novo_status, personagem_id), fetch=False)
        return True

    @staticmethod
    def listar_todos_admin():
        """Lista todos os personagens para admin (com mais informações)"""
        query = """
            SELECT p.*,
                   u.username AS usuario_username,
                   u.nome_completo AS usuario_nome_completo,
                   c.nome_campanha
            FROM personagens p
            LEFT JOIN usuarios u ON u.id = p.id_usuario_jogador
            LEFT JOIN campanhas c ON c.id = p.id_campanha
            ORDER BY p.created_at DESC
        """
        return Database.execute_query(query)

