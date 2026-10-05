# ==========================================
# Vantagens e desvantagens do personagem
# ==========================================

from database import Database
from models.atributos import Atributos

class VantagemDesvantagem:
    """Modelo para a tabela de vantagens e desvantagens"""
    
    # Mapeamento de vantagens para seus efeitos automáticos
    EFEITOS_AUTOMATICOS = {
        'reflexos em combate': {
            'percepcao_extra': 1,
            'descricao': '+1 em Percepção e +1 em todas as defesas'
        },
        'pv extra': {
            'PV_extra': 1,
            'descricao': '+1 em Pontos de Vida'
        },
        'pf extra': {
            'PF_extra': 1,
            'descricao': '+1 em Pontos de Fadiga'
        },
        'sentidos aguçados': {
            'percepcao_extra': 1,
            'descricao': '+1 em Percepção'
        },
        'vontade férrea': {
            'vontade_extra': 1,
            'descricao': '+1 em Vontade'
        },
        'vontade extra': {
            'vontade_extra': 1,
            'descricao': '+1 em Vontade'
        },
    }
    
    @staticmethod
    def _obter_efeitos_vantagem(nome_item):
        """Retorna os efeitos automáticos de uma vantagem"""
        nome_lower = nome_item.lower().strip()
        return VantagemDesvantagem.EFEITOS_AUTOMATICOS.get(nome_lower, {})
    
    @staticmethod
    def criar(personagem_id, nome_item, custo_em_pontos, notas=''):
        """
        Adiciona uma vantagem ou desvantagem e aplica efeitos automáticos.
        
        Se a vantagem tiver efeitos automáticos (como aumentar atributos),
        eles serão aplicados automaticamente.
        """
        # Verifica se a vantagem tem efeitos automáticos
        efeitos = VantagemDesvantagem._obter_efeitos_vantagem(nome_item)
        
        # Aplica efeitos automáticos antes de criar a vantagem
        if efeitos:
            atributos = Atributos.buscar_por_personagem(personagem_id)
            if atributos:
                # Atualiza atributos com os efeitos
                PV_extra = atributos.get('PV_extra', 0) or 0
                PF_extra = atributos.get('PF_extra', 0) or 0
                percepcao_extra = atributos.get('percepcao_extra', 0) or 0
                vontade_extra = atributos.get('vontade_extra', 0) or 0
                
                # Aplica efeitos
                if 'PV_extra' in efeitos:
                    PV_extra += efeitos['PV_extra']
                if 'PF_extra' in efeitos:
                    PF_extra += efeitos['PF_extra']
                if 'percepcao_extra' in efeitos:
                    percepcao_extra += efeitos['percepcao_extra']
                if 'vontade_extra' in efeitos:
                    vontade_extra += efeitos['vontade_extra']
                
                # Atualiza os atributos
                Atributos.atualizar(
                    personagem_id,
                    atributos['ST'],
                    atributos['DX'],
                    atributos['IQ'],
                    atributos['HT'],
                    PV_extra=PV_extra,
                    PF_extra=PF_extra,
                    percepcao_extra=percepcao_extra,
                    vontade_extra=vontade_extra
                )
        
        # Cria a vantagem
        query = """
            INSERT INTO vantagens_desvantagens (personagem_id, nome_item, custo_em_pontos, notas)
            VALUES (%s, %s, %s, %s)
        """
        params = (personagem_id, nome_item, custo_em_pontos, notas)
        return Database.execute_query(query, params, fetch=False)
    
    @staticmethod
    def listar_por_personagem(personagem_id):
        """Lista todas as vantagens/desvantagens de um personagem"""
        query = """
            SELECT * FROM vantagens_desvantagens 
            WHERE personagem_id = %s 
            ORDER BY custo_em_pontos DESC
        """
        return Database.execute_query(query, (personagem_id,))
    
    @staticmethod
    def deletar(vd_id):
        """Remove uma vantagem ou desvantagem (método simples, sem reverter efeitos)"""
        query = "DELETE FROM vantagens_desvantagens WHERE id = %s"
        Database.execute_query(query, (vd_id,), fetch=False)
    
    @staticmethod
    def deletar_com_efeitos(vd_id):
        """
        Remove uma vantagem ou desvantagem e reverte seus efeitos automáticos.
        
        Retorna o nome da vantagem removida para uso externo.
        """
        # Busca a vantagem antes de deletar
        query_busca = "SELECT * FROM vantagens_desvantagens WHERE id = %s"
        result = Database.execute_query(query_busca, (vd_id,))
        
        if not result:
            return None
        
        vantagem = result[0]
        nome_item = vantagem.get('nome_item', '')
        personagem_id = vantagem.get('personagem_id')
        
        # Verifica se tem efeitos para reverter
        efeitos = VantagemDesvantagem._obter_efeitos_vantagem(nome_item)
        
        if efeitos and personagem_id:
            atributos = Atributos.buscar_por_personagem(personagem_id)
            if atributos:
                # Reverte efeitos
                PV_extra = atributos.get('PV_extra', 0) or 0
                PF_extra = atributos.get('PF_extra', 0) or 0
                percepcao_extra = atributos.get('percepcao_extra', 0) or 0
                vontade_extra = atributos.get('vontade_extra', 0) or 0
                
                # Reverte efeitos
                if 'PV_extra' in efeitos:
                    PV_extra = max(0, PV_extra - efeitos['PV_extra'])
                if 'PF_extra' in efeitos:
                    PF_extra = max(0, PF_extra - efeitos['PF_extra'])
                if 'percepcao_extra' in efeitos:
                    percepcao_extra -= efeitos['percepcao_extra']
                if 'vontade_extra' in efeitos:
                    vontade_extra -= efeitos['vontade_extra']
                
                # Atualiza os atributos
                Atributos.atualizar(
                    personagem_id,
                    atributos['ST'],
                    atributos['DX'],
                    atributos['IQ'],
                    atributos['HT'],
                    PV_extra=PV_extra,
                    PF_extra=PF_extra,
                    percepcao_extra=percepcao_extra,
                    vontade_extra=vontade_extra
                )
        
        # Deleta a vantagem
        query = "DELETE FROM vantagens_desvantagens WHERE id = %s"
        Database.execute_query(query, (vd_id,), fetch=False)
        
        return nome_item

