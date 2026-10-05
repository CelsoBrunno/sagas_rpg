# Acesso temporário: o mestre libera outra ficha por um prazo.
# A ficha própria do jogador (id_usuario_jogador) não muda.

from datetime import datetime

from database import Database

_TABELA_PRONTA = False

_CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS acessos_temporarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_personagem INT NOT NULL,
    id_usuario INT NOT NULL,
    expira_em DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_acesso_personagem_usuario (id_personagem, id_usuario),
    CONSTRAINT fk_acesso_temp_personagem FOREIGN KEY (id_personagem)
        REFERENCES personagens(id) ON DELETE CASCADE,
    CONSTRAINT fk_acesso_temp_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""


def _como_data(valor):
    if isinstance(valor, datetime):
        return valor
    if not valor:
        return None
    texto = str(valor)[:16]
    for formato in ('%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M'):
        try:
            return datetime.strptime(texto, formato)
        except ValueError:
            continue
    return None


class AcessoTemporario:

    @staticmethod
    def garantir_tabela():
        global _TABELA_PRONTA
        if _TABELA_PRONTA:
            return
        Database.execute_query(_CRIAR_TABELA, fetch=False)
        _TABELA_PRONTA = True

    @staticmethod
    def liberar(personagem_id, usuario_id, expira_em):
        AcessoTemporario.garantir_tabela()
        Database.execute_query(
            """
            INSERT INTO acessos_temporarios (id_personagem, id_usuario, expira_em)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE expira_em = VALUES(expira_em)
            """,
            (personagem_id, usuario_id, expira_em),
            fetch=False,
        )

    @staticmethod
    def encerrar(personagem_id, usuario_id):
        AcessoTemporario.garantir_tabela()
        Database.execute_query(
            "DELETE FROM acessos_temporarios WHERE id_personagem = %s AND id_usuario = %s",
            (personagem_id, usuario_id),
            fetch=False,
        )

    @staticmethod
    def _buscar(personagem_id, usuario_id):
        AcessoTemporario.garantir_tabela()
        linhas = Database.execute_query(
            """
            SELECT expira_em FROM acessos_temporarios
            WHERE id_personagem = %s AND id_usuario = %s
            """,
            (personagem_id, usuario_id),
        )
        if not linhas:
            return None
        return _como_data(linhas[0].get('expira_em'))

    @staticmethod
    def expira_de(personagem_id, usuario_id):
        """Prazo ainda válido, ou None."""
        if not personagem_id or not usuario_id:
            return None
        expira = AcessoTemporario._buscar(personagem_id, usuario_id)
        if not expira or expira <= datetime.now():
            return None
        return expira

    @staticmethod
    def expirou(personagem_id, usuario_id):
        """Havia um prazo e ele já passou. A linha é removida."""
        if not personagem_id or not usuario_id:
            return False
        expira = AcessoTemporario._buscar(personagem_id, usuario_id)
        if not expira or expira > datetime.now():
            return False
        AcessoTemporario.encerrar(personagem_id, usuario_id)
        return True

    @staticmethod
    def esta_ativo(personagem_id, usuario_id):
        return AcessoTemporario.expira_de(personagem_id, usuario_id) is not None

    @staticmethod
    def mapa_ativos(usuario_id):
        """personagem_id -> datetime, só os prazos que ainda valem."""
        if not usuario_id:
            return {}
        AcessoTemporario.garantir_tabela()
        linhas = Database.execute_query(
            "SELECT id_personagem, expira_em FROM acessos_temporarios WHERE id_usuario = %s",
            (usuario_id,),
        ) or []
        agora = datetime.now()
        ativos = {}
        for linha in linhas:
            expira = _como_data(linha.get('expira_em'))
            if not expira or expira <= agora:
                AcessoTemporario.encerrar(linha['id_personagem'], usuario_id)
                continue
            ativos[linha['id_personagem']] = expira
        return ativos

    @staticmethod
    def listar_ativos(personagem_id):
        AcessoTemporario.garantir_tabela()
        linhas = Database.execute_query(
            """
            SELECT a.id_usuario, a.expira_em, u.username, u.nome_completo
            FROM acessos_temporarios a
            JOIN usuarios u ON u.id = a.id_usuario
            WHERE a.id_personagem = %s
            ORDER BY a.expira_em
            """,
            (personagem_id,),
        ) or []
        agora = datetime.now()
        ativos = []
        for linha in linhas:
            expira = _como_data(linha.get('expira_em'))
            if not expira or expira <= agora:
                AcessoTemporario.encerrar(personagem_id, linha['id_usuario'])
                continue
            linha['expira_em'] = expira
            ativos.append(linha)
        return ativos
