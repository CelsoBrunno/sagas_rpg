# ==========================================
# Sistema de Campanha GURPS - Modelo de Raças
# ==========================================

from database import Database

class Raca:
    """Modelo para a tabela de raças"""
    
    @staticmethod
    def criar(dados):
        """Cria uma nova raça"""
        query = """
            INSERT INTO racas 
            (nome, descricao, bonus_st, bonus_dx, bonus_iq, bonus_ht,
             bonus_pv_extra, bonus_pf_extra, bonus_percepcao_extra, bonus_vontade_extra,
             custo_em_pontos, vantagens_automaticas, pericias_automaticas, observacoes, is_active, id_campanha)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            dados.get('nome'),
            dados.get('descricao'),
            dados.get('bonus_st', 0),
            dados.get('bonus_dx', 0),
            dados.get('bonus_iq', 0),
            dados.get('bonus_ht', 0),
            dados.get('bonus_pv_extra', 0),
            dados.get('bonus_pf_extra', 0),
            dados.get('bonus_percepcao_extra', 0),
            dados.get('bonus_vontade_extra', 0),
            dados.get('custo_em_pontos', 0),
            dados.get('vantagens_automaticas'),
            dados.get('pericias_automaticas'),
            dados.get('observacoes'),
            dados.get('is_active', True),
            dados.get('id_campanha')
        )
        return Database.execute_query(query, params, fetch=False)
    
    @staticmethod
    def listar_todas():
        """Lista todas as raças"""
        query = "SELECT * FROM racas ORDER BY nome"
        return Database.execute_query(query)
    
    @staticmethod
    def listar_por_campanha(campanha_id):
        """Lista as raças de uma campanha"""
        query = "SELECT * FROM racas WHERE id_campanha = %s ORDER BY nome"
        return Database.execute_query(query, (campanha_id,))
    
    @staticmethod
    def listar_ativas():
        """Lista apenas raças ativas"""
        query = "SELECT * FROM racas WHERE is_active = TRUE ORDER BY nome"
        return Database.execute_query(query)
    
    @staticmethod
    def buscar_por_id(raca_id):
        """Busca uma raça por ID"""
        query = "SELECT * FROM racas WHERE id = %s"
        result = Database.execute_query(query, (raca_id,))
        return result[0] if result else None
    
    @staticmethod
    def buscar_por_nome(nome):
        """Busca uma raça por nome"""
        query = "SELECT * FROM racas WHERE nome = %s"
        result = Database.execute_query(query, (nome,))
        return result[0] if result else None
    
    @staticmethod
    def atualizar(raca_id, dados):
        """Atualiza uma raça"""
        query = """
            UPDATE racas 
            SET nome = %s, descricao = %s, bonus_st = %s, bonus_dx = %s, bonus_iq = %s, bonus_ht = %s,
                bonus_pv_extra = %s, bonus_pf_extra = %s, bonus_percepcao_extra = %s, bonus_vontade_extra = %s,
                custo_em_pontos = %s, vantagens_automaticas = %s, pericias_automaticas = %s,
                observacoes = %s, is_active = %s
            WHERE id = %s
        """
        params = (
            dados.get('nome'),
            dados.get('descricao'),
            dados.get('bonus_st', 0),
            dados.get('bonus_dx', 0),
            dados.get('bonus_iq', 0),
            dados.get('bonus_ht', 0),
            dados.get('bonus_pv_extra', 0),
            dados.get('bonus_pf_extra', 0),
            dados.get('bonus_percepcao_extra', 0),
            dados.get('bonus_vontade_extra', 0),
            dados.get('custo_em_pontos', 0),
            dados.get('vantagens_automaticas'),
            dados.get('pericias_automaticas'),
            dados.get('observacoes'),
            dados.get('is_active', True),
            raca_id
        )
        Database.execute_query(query, params, fetch=False)
    
    @staticmethod
    def deletar(raca_id):
        """Deleta uma raça (soft delete - marca como inativa)"""
        query = "UPDATE racas SET is_active = FALSE WHERE id = %s"
        Database.execute_query(query, (raca_id,), fetch=False)
    
    @staticmethod
    def obter_bonus(raca_id):
        """Retorna os bônus de uma raça em formato de dicionário"""
        raca = Raca.buscar_por_id(raca_id)
        if not raca:
            return {}
        
        return {
            'bonus_st': raca.get('bonus_st', 0) or 0,
            'bonus_dx': raca.get('bonus_dx', 0) or 0,
            'bonus_iq': raca.get('bonus_iq', 0) or 0,
            'bonus_ht': raca.get('bonus_ht', 0) or 0,
            'bonus_pv_extra': raca.get('bonus_pv_extra', 0) or 0,
            'bonus_pf_extra': raca.get('bonus_pf_extra', 0) or 0,
            'bonus_percepcao_extra': raca.get('bonus_percepcao_extra', 0) or 0,
            'bonus_vontade_extra': raca.get('bonus_vontade_extra', 0) or 0,
            'custo_em_pontos': raca.get('custo_em_pontos', 0) or 0,
            'vantagens_automaticas': raca.get('vantagens_automaticas'),
            'pericias_automaticas': raca.get('pericias_automaticas')
        }

