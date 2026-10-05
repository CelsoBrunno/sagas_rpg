# ==========================================
# Bônus compartilhados de raça e classe
# ==========================================

from database import Database

TABELAS_BONUS = frozenset({'racas', 'classes'})


class BonusModelo:
    """CRUD das tabelas de raça e classe. A tabela não vem do usuário."""

    tabela = None

    @classmethod
    def _tabela(cls):
        if cls.tabela not in TABELAS_BONUS:
            raise ValueError('Tabela de bônus inválida')
        return cls.tabela

    @classmethod
    def _params_bonus(cls, dados, registro_id=None):
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
        )
        if registro_id is None:
            return params + (dados.get('id_campanha'),)
        return params + (registro_id,)

    @classmethod
    def criar(cls, dados):
        tabela = cls._tabela()
        query = f"""
            INSERT INTO {tabela}
            (nome, descricao, bonus_st, bonus_dx, bonus_iq, bonus_ht,
             bonus_pv_extra, bonus_pf_extra, bonus_percepcao_extra, bonus_vontade_extra,
             custo_em_pontos, vantagens_automaticas, pericias_automaticas, observacoes, is_active, id_campanha)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return Database.execute_query(query, cls._params_bonus(dados), fetch=False)

    @classmethod
    def listar_todas(cls):
        tabela = cls._tabela()
        return Database.execute_query(f"SELECT * FROM {tabela} ORDER BY nome")

    @classmethod
    def listar_por_campanha(cls, campanha_id):
        tabela = cls._tabela()
        return Database.execute_query(
            f"SELECT * FROM {tabela} WHERE id_campanha = %s ORDER BY nome",
            (campanha_id,),
        )

    @classmethod
    def listar_ativas(cls):
        tabela = cls._tabela()
        return Database.execute_query(
            f"SELECT * FROM {tabela} WHERE is_active = TRUE ORDER BY nome"
        )

    @classmethod
    def buscar_por_id(cls, registro_id):
        tabela = cls._tabela()
        result = Database.execute_query(
            f"SELECT * FROM {tabela} WHERE id = %s",
            (registro_id,),
        )
        return result[0] if result else None

    @classmethod
    def buscar_por_nome(cls, nome):
        tabela = cls._tabela()
        result = Database.execute_query(
            f"SELECT * FROM {tabela} WHERE nome = %s",
            (nome,),
        )
        return result[0] if result else None

    @classmethod
    def atualizar(cls, registro_id, dados):
        tabela = cls._tabela()
        query = f"""
            UPDATE {tabela}
            SET nome = %s, descricao = %s, bonus_st = %s, bonus_dx = %s, bonus_iq = %s, bonus_ht = %s,
                bonus_pv_extra = %s, bonus_pf_extra = %s, bonus_percepcao_extra = %s, bonus_vontade_extra = %s,
                custo_em_pontos = %s, vantagens_automaticas = %s, pericias_automaticas = %s,
                observacoes = %s, is_active = %s
            WHERE id = %s
        """
        Database.execute_query(query, cls._params_bonus(dados, registro_id), fetch=False)

    @classmethod
    def deletar(cls, registro_id):
        tabela = cls._tabela()
        Database.execute_query(
            f"UPDATE {tabela} SET is_active = FALSE WHERE id = %s",
            (registro_id,),
            fetch=False,
        )

    @classmethod
    def obter_bonus(cls, registro_id):
        registro = cls.buscar_por_id(registro_id)
        if not registro:
            return {}
        return {
            'bonus_st': registro.get('bonus_st', 0) or 0,
            'bonus_dx': registro.get('bonus_dx', 0) or 0,
            'bonus_iq': registro.get('bonus_iq', 0) or 0,
            'bonus_ht': registro.get('bonus_ht', 0) or 0,
            'bonus_pv_extra': registro.get('bonus_pv_extra', 0) or 0,
            'bonus_pf_extra': registro.get('bonus_pf_extra', 0) or 0,
            'bonus_percepcao_extra': registro.get('bonus_percepcao_extra', 0) or 0,
            'bonus_vontade_extra': registro.get('bonus_vontade_extra', 0) or 0,
            'custo_em_pontos': registro.get('custo_em_pontos', 0) or 0,
            'vantagens_automaticas': registro.get('vantagens_automaticas'),
            'pericias_automaticas': registro.get('pericias_automaticas'),
        }
