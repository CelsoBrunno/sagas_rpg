# ==========================================
# Perícias do personagem
# ==========================================

from database import Database
from models.atributos import Atributos

class Pericia:
    """Modelo para a tabela de perícias"""
    
    @staticmethod
    def criar(personagem_id, nome_pericia, atributo_base, dificuldade, pontos_investidos):
        """Adiciona uma perícia"""
        # Busca atributos reais do personagem
        atributos = Atributos.buscar_por_personagem(personagem_id)
        if atributos:
            atributo_valor = atributos.get(atributo_base, 10)
        else:
            atributo_valor = 10
        
        # Calcula o nível de habilidade usando atributo real
        nivel = Pericia._calcular_nivel_habilidade(
            atributo_valor, dificuldade, pontos_investidos
        )
        
        query = """
            INSERT INTO pericias (personagem_id, nome_pericia, atributo_base, dificuldade, pontos_investidos, nivel_habilidade_calculado)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (personagem_id, nome_pericia, atributo_base, dificuldade, pontos_investidos, nivel)
        return Database.execute_query(query, params, fetch=False)
    
    @staticmethod
    def listar_por_personagem(personagem_id):
        """Lista todas as perícias de um personagem"""
        query = """
            SELECT * FROM pericias 
            WHERE personagem_id = %s 
            ORDER BY nome_pericia
        """
        return Database.execute_query(query, (personagem_id,))
    
    @staticmethod
    def atualizar(pericia_id, pontos_investidos):
        """Atualiza uma perícia"""
        # Busca a perícia para obter os dados necessários
        query_busca = "SELECT * FROM pericias WHERE id = %s"
        result = Database.execute_query(query_busca, (pericia_id,))
        
        if not result:
            return
        
        pericia = result[0]
        personagem_id = pericia['personagem_id']
        atributo_base = pericia['atributo_base']
        
        # Busca atributos reais do personagem
        atributos = Atributos.buscar_por_personagem(personagem_id)
        if atributos:
            atributo_valor = atributos.get(atributo_base, 10)
        else:
            atributo_valor = 10
        
        nivel = Pericia._calcular_nivel_habilidade(
            atributo_valor,
            pericia['dificuldade'],
            pontos_investidos
        )
        
        query = """
            UPDATE pericias 
            SET pontos_investidos = %s, nivel_habilidade_calculado = %s
            WHERE id = %s
        """
        params = (pontos_investidos, nivel, pericia_id)
        Database.execute_query(query, params, fetch=False)
    
    @staticmethod
    def deletar(pericia_id):
        """Remove uma perícia"""
        query = "DELETE FROM pericias WHERE id = %s"
        Database.execute_query(query, (pericia_id,), fetch=False)
    
    @staticmethod
    def _calcular_nivel_habilidade(atributo_valor, dificuldade, pontos):
        """Calcula o NH (nível de habilidade) seguindo a tabela oficial do GURPS 4e.
        
        Regras gerais:
            - Cada dificuldade possui um ajuste base quando não há pontos investidos
            - Pontos investidos seguem marcos (1, 2, 4, 8) e, após 8, cada +4 pontos eleva o NH em +1
        """
        if atributo_valor is None:
            atributo_valor = 10
        
        dificuldade = (dificuldade or '').upper()
        
        ajustes_sem_pontos = {
            'F': -4,   # Fácil
            'M': -5,   # Média
            'D': -6,   # Difícil
            'MD': -7   # Muito Difícil
        }
        
        marcos = {
            'F': [(1, 0), (2, 1), (4, 2), (8, 3)],
            'M': [(1, -1), (2, 0), (4, 1), (8, 2)],
            'D': [(1, -2), (2, -1), (4, 0), (8, 1)],
            'MD': [(1, -3), (2, -2), (4, -1), (8, 0)]
        }
        
        if pontos is None:
            pontos = 0
        
        if pontos <= 0:
            ajuste = ajustes_sem_pontos.get(dificuldade, -5)
            return atributo_valor + ajuste
        
        marcos_dificuldade = marcos.get(dificuldade, marcos['M'])
        
        for limite, ajuste in marcos_dificuldade:
            if pontos <= limite:
                return atributo_valor + ajuste
        
        # Pontos acima do último marco (>= 8)
        limite_base, ajuste_base = marcos_dificuldade[-1]
        excesso = pontos - limite_base
        incremento = excesso // 4  # a cada +4 pontos, +1 nível
        
        return atributo_valor + ajuste_base + incremento

