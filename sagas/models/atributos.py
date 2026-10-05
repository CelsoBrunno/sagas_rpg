# ==========================================
# Atributos do personagem
# ==========================================

from config import Config
from database import Database

class Atributos:
    """Modelo para a tabela de atributos"""
    
    @staticmethod
    def criar(personagem_id, ST=10, DX=10, IQ=10, HT=10, PV_extra=0, PF_extra=0, percepcao_extra=0, vontade_extra=0):
        """Cria os atributos de um personagem"""
        # Calcula o custo total dos atributos
        custo = Atributos._calcular_custo_atributos(ST, DX, IQ, HT, PV_extra, PF_extra, percepcao_extra, vontade_extra)
        
        query = """
            INSERT INTO atributos (personagem_id, ST, DX, IQ, HT, custo_total_atributos, PV_extra, PF_extra, percepcao_extra, vontade_extra)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (personagem_id, ST, DX, IQ, HT, custo, PV_extra, PF_extra, percepcao_extra, vontade_extra)
        return Database.execute_query(query, params, fetch=False)
    
    @staticmethod
    def buscar_por_personagem(personagem_id):
        """Busca os atributos de um personagem"""
        query = "SELECT * FROM atributos WHERE personagem_id = %s"
        result = Database.execute_query(query, (personagem_id,))
        return result[0] if result else None
    
    @staticmethod
    def atualizar(personagem_id, ST, DX, IQ, HT, PV_extra=None, PF_extra=None, percepcao_extra=None, vontade_extra=None):
        """Atualiza os atributos de um personagem"""
        # Se extras não foram fornecidos, mantém os valores atuais
        atributos_atual = Atributos.buscar_por_personagem(personagem_id)
        if atributos_atual:
            if PV_extra is None:
                PV_extra = atributos_atual.get('PV_extra', 0) or 0
            if PF_extra is None:
                PF_extra = atributos_atual.get('PF_extra', 0) or 0
            if percepcao_extra is None:
                percepcao_extra = atributos_atual.get('percepcao_extra', 0) or 0
            if vontade_extra is None:
                vontade_extra = atributos_atual.get('vontade_extra', 0) or 0
        else:
            PV_extra = PV_extra or 0
            PF_extra = PF_extra or 0
            percepcao_extra = percepcao_extra or 0
            vontade_extra = vontade_extra or 0
        
        # Valida limites
        # PV máximo = ST*2, então PV_extra máximo = ST
        PV_extra = max(0, min(int(PV_extra), ST))
        # PF máximo = IQ*2 conforme solicitado, então PF_extra máximo = IQ
        PF_extra = max(0, min(int(PF_extra), IQ))
        # Percepção e Vontade podem ser aumentadas ou reduzidas (sem limite específico, mas geralmente ±4)
        percepcao_extra = int(percepcao_extra)
        vontade_extra = int(vontade_extra)
        
        custo = Atributos._calcular_custo_atributos(ST, DX, IQ, HT, PV_extra, PF_extra, percepcao_extra, vontade_extra)
        
        query = """
            UPDATE atributos 
            SET ST = %s, DX = %s, IQ = %s, HT = %s, custo_total_atributos = %s, 
                PV_extra = %s, PF_extra = %s, percepcao_extra = %s, vontade_extra = %s
            WHERE personagem_id = %s
        """
        params = (ST, DX, IQ, HT, custo, PV_extra, PF_extra, percepcao_extra, vontade_extra, personagem_id)
        Database.execute_query(query, params, fetch=False)
    
    @staticmethod
    def calcular_atributos_derivados(atributos, vantagens=None):
        """
        Calcula atributos derivados baseado nos atributos básicos e bônus de vantagens.
        
        Args:
            atributos: Dict com atributos básicos
            vantagens: Lista de vantagens do personagem (opcional)
        """
        ST = atributos['ST']
        DX = atributos['DX']
        IQ = atributos['IQ']
        HT = atributos['HT']
        PV_extra = atributos.get('PV_extra', 0) or 0
        PF_extra = atributos.get('PF_extra', 0) or 0
        
        # Velocidade Básica (Vb)
        velocidade_basica = round((DX + HT) / Config.MULTIPLICADOR_VELOCIDADE_BASICA, 1)
        
        # Pontos de Vida (PV) = ST + PV_extra (máximo ST*2)
        PV = ST + PV_extra
        
        # Pontos de Fadiga (PF) = HT + PF_extra (máximo IQ*2 conforme solicitado)
        # Base é HT, mas pode ser aumentado até IQ*2
        PF = HT + PF_extra
        
        # Percepção e Vontade (base = IQ, podem ser aumentadas/reduzidas)
        percepcao_extra = atributos.get('percepcao_extra', 0) or 0
        vontade_extra = atributos.get('vontade_extra', 0) or 0
        
        # Bônus de vantagens
        bonus_esquiva = 0
        bonus_aparar = 0
        bonus_bloqueio = 0
        
        if vantagens:
            for vantagem in vantagens:
                nome = vantagem.get('nome_item', '').lower()
                # Reflexos em Combate: +1 Percepção (já aplicado via percepcao_extra) e +1 em todas as defesas
                if 'reflexos em combate' in nome:
                    bonus_esquiva += 1
                    bonus_aparar += 1
                    bonus_bloqueio += 1
                # Esquiva Ampliada: +1 Esquiva
                elif 'esquiva ampliada' in nome:
                    bonus_esquiva += 1
                # Aparar Ampliado: +1 Aparar
                elif 'aparar ampliado' in nome:
                    bonus_aparar += 1
                # Bloqueio Ampliado: +1 Bloqueio
                elif 'bloqueio ampliado' in nome:
                    bonus_bloqueio += 1
        
        percepcao = IQ + percepcao_extra
        vontade = IQ + vontade_extra
        
        # Esquiva - Velocidade Básica + 3 + bônus de Percepção extra + bônus de vantagens
        # Cada ponto de Percepção extra aumenta Esquiva em 1
        esquiva = int(velocidade_basica) + Config.ESQUIVA_BASE + percepcao_extra + bonus_esquiva
        
        # Peso Máximo (PM) - ST * 15
        PM = ST * 15
        
        # Golpe de Ponta (GPD) e Golpe em Balanço (BAL) - baseado em ST
        gpd = Atributos._calcular_golpe_ponta(ST)
        bal = Atributos._calcular_golpe_balanco(ST)
        
        return {
            'velocidade_basica': velocidade_basica,
            'PV': PV,
            'PF': PF,
            'percepcao': percepcao,
            'vontade': vontade,
            'esquiva': esquiva,
            'PM': PM,
            'gpd': gpd,
            'bal': bal,
            'bonus_aparar': bonus_aparar,
            'bonus_bloqueio': bonus_bloqueio,
            'deslocamento': int(velocidade_basica),
            'aparar': int(DX / 2) + Config.APARAR_BASE + bonus_aparar,
            'bloqueio': Config.BLOQUEIO_BASE + bonus_bloqueio,
        }
    
    @staticmethod
    def _calcular_golpe_ponta(ST):
        """
        Calcula Golpe de Ponta (GdP) baseado em ST.
        Tabela GURPS 4ª Edição.
        """
        # Tabela de GdP baseada em ST
        tabela_gpd = {
            1: '1d-6', 2: '1d-6', 3: '1d-5', 4: '1d-5',
            5: '1d-4', 6: '1d-4', 7: '1d-3', 8: '1d-3',
            9: '1d-2', 10: '1d-2', 11: '1d-1', 12: '1d-1',
            13: '1d', 14: '1d', 15: '1d+1', 16: '1d+1',
            17: '1d+2', 18: '1d+2', 19: '2d-1', 20: '2d-1',
            21: '2d', 22: '2d', 23: '2d+1', 24: '2d+1',
            25: '2d+2', 26: '2d+2', 27: '3d-1', 28: '3d-1',
            29: '3d', 30: '3d', 31: '3d+1', 32: '3d+1',
            33: '3d+2', 34: '3d+2', 35: '4d-1', 36: '4d-1',
            37: '4d', 38: '4d', 39: '4d+1', 40: '4d+1'
        }
        
        if ST <= 40:
            return tabela_gpd.get(ST, '1d')
        
        # Para ST > 40, calcula baseado na progressão
        # Cada 10 pontos de ST acima de 40 adiciona aproximadamente 1d
        # Fórmula aproximada baseada na tabela
        st_base = 40
        st_excesso = ST - st_base
        dados_extra = st_excesso // 10
        st_resto = st_excesso % 10
        
        # Base em 40: 4d+1
        if st_resto == 0:
            return f'{4 + dados_extra}d+1'
        elif st_resto <= 2:
            return f'{4 + dados_extra}d+2'
        elif st_resto <= 4:
            return f'{4 + dados_extra + 1}d-1'
        elif st_resto <= 6:
            return f'{4 + dados_extra + 1}d'
        elif st_resto <= 8:
            return f'{4 + dados_extra + 1}d+1'
        else:
            return f'{4 + dados_extra + 1}d+2'
    
    @staticmethod
    def _calcular_golpe_balanco(ST):
        """
        Calcula Golpe em Balanço (Bal.) baseado em ST.
        Tabela GURPS 4ª Edição.
        """
        # Tabela de Bal baseada em ST
        tabela_bal = {
            1: '1d-5', 2: '1d-5', 3: '1d-4', 4: '1d-4',
            5: '1d-3', 6: '1d-3', 7: '1d-2', 8: '1d-2',
            9: '1d-1', 10: '1d', 11: '1d+1', 12: '1d+2',
            13: '2d-1', 14: '2d', 15: '2d+1', 16: '2d+2',
            17: '3d-1', 18: '3d', 19: '3d+1', 20: '3d+2',
            21: '4d-1', 22: '4d', 23: '4d+1', 24: '4d+2',
            25: '5d-1', 26: '5d', 27: '5d+1', 28: '5d+1',
            29: '5d+2', 30: '5d+2', 31: '6d-1', 32: '6d-1',
            33: '6d', 34: '6d', 35: '6d+1', 36: '6d+1',
            37: '6d+2', 38: '6d+2', 39: '7d-1', 40: '7d-1'
        }
        
        if ST <= 40:
            return tabela_bal.get(ST, '1d')
        
        # Para ST > 40, calcula baseado na progressão
        # Cada 10 pontos de ST acima de 40 adiciona aproximadamente 1d
        st_base = 40
        st_excesso = ST - st_base
        dados_extra = st_excesso // 10
        st_resto = st_excesso % 10
        
        # Base em 40: 7d-1
        if st_resto == 0:
            return f'{7 + dados_extra}d-1'
        elif st_resto <= 2:
            return f'{7 + dados_extra}d'
        elif st_resto <= 4:
            return f'{7 + dados_extra}d+1'
        elif st_resto <= 6:
            return f'{7 + dados_extra + 1}d-1'
        elif st_resto <= 8:
            return f'{7 + dados_extra + 1}d'
        else:
            return f'{7 + dados_extra + 1}d+1'
    
    @staticmethod
    def _calcular_custo_atributos(ST, DX, IQ, HT, PV_extra=0, PF_extra=0, percepcao_extra=0, vontade_extra=0):
        """
        Calcula o custo total em pontos dos atributos.
        
        Regras GURPS 4ª Edição:
        - ST e HT: 10 pontos por nível acima/abaixo de 10
        - DX e IQ: 20 pontos por nível acima/abaixo de 10
        - PV extra: 2 pontos por ponto (máximo ST*2)
        - PF extra: 2 pontos por ponto (máximo IQ*2)
        - Percepção extra: 5 pontos por nível acima/abaixo de IQ
        - Vontade extra: 5 pontos por nível acima/abaixo de IQ
        """
        custo_ST = Atributos._custo_individual(ST, custo_por_nivel=10)
        custo_DX = Atributos._custo_individual(DX, custo_por_nivel=20)
        custo_IQ = Atributos._custo_individual(IQ, custo_por_nivel=20)
        custo_HT = Atributos._custo_individual(HT, custo_por_nivel=10)
        
        # Custo de PV e PF extras (2 pontos por ponto)
        custo_PV_extra = PV_extra * 2
        custo_PF_extra = PF_extra * 2
        
        # Custo de Percepção e Vontade extras (5 pontos por nível)
        custo_percepcao_extra = percepcao_extra * 5
        custo_vontade_extra = vontade_extra * 5
        
        return custo_ST + custo_DX + custo_IQ + custo_HT + custo_PV_extra + custo_PF_extra + custo_percepcao_extra + custo_vontade_extra
    
    @staticmethod
    def _custo_individual(valor, custo_por_nivel):
        """
        Calcula o custo individual de um atributo.
        
        Args:
            valor: Valor do atributo (1-∞)
            custo_por_nivel: Custo por nível acima/abaixo de 10 (10 para ST/HT, 20 para DX/IQ)
        
        Returns:
            Custo em pontos (negativo para valores abaixo de 10, positivo para acima)
        """
        if valor <= 8:
            # Para valores 8 ou menos: -80 pontos base + ajuste por nível
            # Valor 8 = -80, valor 7 = -70, valor 6 = -60, etc.
            return -80 + (valor - 8) * custo_por_nivel
        elif valor == 9:
            # Valor 9 = -10 pontos (independente do atributo)
            return -10
        elif valor == 10:
            # Valor 10 = 0 pontos (padrão humano)
            return 0
        else:
            # Valores acima de 10: custo varia por atributo
            # ST/HT: +10 por nível, DX/IQ: +20 por nível
            return (valor - 10) * custo_por_nivel

