# ==========================================
# Sistema de Campanha GURPS - Modelos
# ==========================================

from database import Database

class Personagem:
    """Modelo para a tabela de personagens"""
    
    @staticmethod
    def criar(dados):
        """Cria um novo personagem"""
        # Verifica se categoria existe no schema
        try:
            query = """
                INSERT INTO personagens 
                (nome, jogador_nome, raca, categoria, pontos_base, pontos_desvantagens_max, biografia, tipo, status, id_usuario_jogador, raca_id, classe_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                dados.get('classe_id')
            )
            return Database.execute_query(query, params, fetch=False)
        except:
            # Fallback se categoria não existir
            query = """
                INSERT INTO personagens 
                (nome, jogador_nome, raca, pontos_base, pontos_desvantagens_max, biografia, tipo, status, id_usuario_jogador, raca_id, classe_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                dados.get('nome'),
                dados.get('jogador_nome'),
                dados.get('raca'),
                dados.get('pontos_base', 0),
                dados.get('pontos_desvantagens_max', 0),
                dados.get('biografia'),
                dados.get('tipo', 'PJ'),
                dados.get('status', 'Ativo'),
                dados.get('id_usuario_jogador'),
                dados.get('raca_id'),
                dados.get('classe_id')
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
    def atualizar(personagem_id, dados):
        """Atualiza um personagem"""
        # Tenta atualizar com categoria
        try:
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
        except:
            # Fallback se categoria não existir
            query = """
                UPDATE personagens 
                SET nome = %s, jogador_nome = %s, raca = %s, pontos_base = %s,
                    pontos_desvantagens_max = %s, biografia = %s, status = %s
                WHERE id = %s
            """
            params = (
                dados.get('nome'),
                dados.get('jogador_nome'),
                dados.get('raca'),
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
        velocidade_basica = round((DX + HT) / 4, 1)
        
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
        esquiva = int(velocidade_basica) + 3 + percepcao_extra + bonus_esquiva
        
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
            'bonus_bloqueio': bonus_bloqueio
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
            'VD': -7   # Muito Difícil
        }
        
        marcos = {
            'F': [(1, 0), (2, 1), (4, 2), (8, 3)],
            'M': [(1, -1), (2, 0), (4, 1), (8, 2)],
            'D': [(1, -2), (2, -1), (4, 0), (8, 1)],
            'VD': [(1, -3), (2, -2), (4, -1), (8, 0)]
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

