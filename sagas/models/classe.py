# ==========================================
# Sistema de Campanha GURPS - Modelo de Classes
# ==========================================

from database import Database

class Classe:
    """Modelo para a tabela de classes"""
    
    @staticmethod
    def criar(dados):
        """Cria uma nova classe"""
        query = """
            INSERT INTO classes 
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
        """Lista todas as classes"""
        query = "SELECT * FROM classes ORDER BY nome"
        return Database.execute_query(query)
    
    @staticmethod
    def listar_por_campanha(campanha_id):
        """Lista as classes de uma campanha"""
        query = "SELECT * FROM classes WHERE id_campanha = %s ORDER BY nome"
        return Database.execute_query(query, (campanha_id,))
    
    @staticmethod
    def listar_ativas():
        """Lista apenas classes ativas"""
        query = "SELECT * FROM classes WHERE is_active = TRUE ORDER BY nome"
        return Database.execute_query(query)
    
    @staticmethod
    def buscar_por_id(classe_id):
        """Busca uma classe por ID"""
        query = "SELECT * FROM classes WHERE id = %s"
        result = Database.execute_query(query, (classe_id,))
        return result[0] if result else None
    
    @staticmethod
    def buscar_por_nome(nome):
        """Busca uma classe por nome"""
        query = "SELECT * FROM classes WHERE nome = %s"
        result = Database.execute_query(query, (nome,))
        return result[0] if result else None
    
    @staticmethod
    def atualizar(classe_id, dados):
        """Atualiza uma classe"""
        query = """
            UPDATE classes 
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
            classe_id
        )
        Database.execute_query(query, params, fetch=False)
    
    @staticmethod
    def deletar(classe_id):
        """Deleta uma classe (soft delete - marca como inativa)"""
        query = "UPDATE classes SET is_active = FALSE WHERE id = %s"
        Database.execute_query(query, (classe_id,), fetch=False)
    
    @staticmethod
    def obter_bonus(classe_id):
        """Retorna os bônus de uma classe em formato de dicionário"""
        classe = Classe.buscar_por_id(classe_id)
        if not classe:
            return {}
        
        return {
            'bonus_st': classe.get('bonus_st', 0) or 0,
            'bonus_dx': classe.get('bonus_dx', 0) or 0,
            'bonus_iq': classe.get('bonus_iq', 0) or 0,
            'bonus_ht': classe.get('bonus_ht', 0) or 0,
            'bonus_pv_extra': classe.get('bonus_pv_extra', 0) or 0,
            'bonus_pf_extra': classe.get('bonus_pf_extra', 0) or 0,
            'bonus_percepcao_extra': classe.get('bonus_percepcao_extra', 0) or 0,
            'bonus_vontade_extra': classe.get('bonus_vontade_extra', 0) or 0,
            'custo_em_pontos': classe.get('custo_em_pontos', 0) or 0,
            'vantagens_automaticas': classe.get('vantagens_automaticas'),
            'pericias_automaticas': classe.get('pericias_automaticas')
        }

