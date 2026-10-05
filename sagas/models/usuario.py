# ==========================================
# Módulo 5: Modelo de Usuários e Permissões
# ==========================================

import hashlib

from werkzeug.security import check_password_hash, generate_password_hash

from database import Database

class Usuario:
    """Modelo para a tabela de usuários"""
    
    @staticmethod
    def criar(dados):
        """Cria um novo usuário com senha hasheada"""
        senha_hash = Usuario.hash_password(dados['password'])
        
        query = """
            INSERT INTO usuarios 
            (username, email, hashed_password, role, nome_completo, pontos_disponiveis)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            dados.get('username'),
            dados.get('email'),
            senha_hash,
            dados.get('role', 'usuario'),
            dados.get('nome_completo'),
            dados.get('pontos_disponiveis', 0)
        )
        return Database.execute_query(query, params, fetch=False)
    
    @staticmethod
    def buscar_por_username(username):
        """Busca um usuário por username"""
        query = "SELECT * FROM usuarios WHERE username = %s AND is_active = TRUE"
        result = Database.execute_query(query, (username,))
        return result[0] if result else None
    
    @staticmethod
    def buscar_por_id(user_id):
        """Busca um usuário por ID"""
        query = "SELECT * FROM usuarios WHERE id = %s"
        result = Database.execute_query(query, (user_id,))
        return result[0] if result else None
    
    @staticmethod
    def senha_legado(hashed_password):
        """Hash MD5 antigo: 32 caracteres hexadecimais."""
        if not hashed_password or len(hashed_password) != 32:
            return False
        return all(c in '0123456789abcdef' for c in hashed_password.lower())

    @staticmethod
    def verificar_senha(hashed_password, senha_plain):
        """Aceita o hash novo e o MD5 antigo, para não derrubar logins já gravados."""
        if not hashed_password or senha_plain is None:
            return False
        if Usuario.senha_legado(hashed_password):
            return hashlib.md5(senha_plain.encode()).hexdigest() == hashed_password
        try:
            return check_password_hash(hashed_password, senha_plain)
        except (TypeError, ValueError):
            return False

    @staticmethod
    def hash_password(senha_plain):
        """Hash com sal. pbkdf2 cabe em hashed_password VARCHAR(255)."""
        return generate_password_hash(senha_plain, method='pbkdf2:sha256')

    @staticmethod
    def definir_senha(user_id, senha_plain):
        """Grava um hash novo. Usado no cadastro e para trocar MD5 no login."""
        query = "UPDATE usuarios SET hashed_password = %s WHERE id = %s"
        Database.execute_query(query, (Usuario.hash_password(senha_plain), user_id), fetch=False)
    
    @staticmethod
    def atualizar_last_login(user_id):
        """Atualiza o timestamp do último login"""
        query = "UPDATE usuarios SET last_login = NOW() WHERE id = %s"
        Database.execute_query(query, (user_id,), fetch=False)
    
    @staticmethod
    def listar_todos():
        """Lista todos os usuários"""
        query = "SELECT id, username, email, role, nome_completo, pontos_disponiveis, is_active, created_at FROM usuarios ORDER BY username"
        return Database.execute_query(query)
    
    @staticmethod
    def atualizar_role(user_id, novo_role):
        """Atualiza o papel/permissão de um usuário"""
        query = "UPDATE usuarios SET role = %s WHERE id = %s"
        Database.execute_query(query, (novo_role, user_id), fetch=False)
    
    @staticmethod
    def is_admin(user_id):
        """Verifica se o usuário é admin"""
        query = "SELECT role FROM usuarios WHERE id = %s"
        result = Database.execute_query(query, (user_id,))
        if result:
            return result[0]['role'] == 'admin'
        return False

    @staticmethod
    def atualizar_status(user_id, is_active):
        """Atualiza o status ativo/inativo de um usuário"""
        query = "UPDATE usuarios SET is_active = %s WHERE id = %s"
        Database.execute_query(query, (bool(is_active), user_id), fetch=False)

    @staticmethod
    def atualizar(user_id, dados):
        """Atualiza dados de um usuário"""
        updates = []
        params = []
        
        if 'role' in dados:
            updates.append("role = %s")
            params.append(dados['role'])
        if 'is_active' in dados:
            updates.append("is_active = %s")
            params.append(bool(dados['is_active']))
        if 'nome_completo' in dados:
            updates.append("nome_completo = %s")
            params.append(dados['nome_completo'])
        if 'email' in dados:
            updates.append("email = %s")
            params.append(dados['email'])
        if 'pontos_disponiveis' in dados:
            updates.append("pontos_disponiveis = %s")
            params.append(int(dados['pontos_disponiveis']))
        
        if not updates:
            return False
        
        params.append(user_id)
        query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = %s"
        Database.execute_query(query, params, fetch=False)
        return True
    
    @staticmethod
    def adicionar_pontos(user_id, quantidade):
        """Adiciona pontos a um usuário"""
        query = """
            UPDATE usuarios 
            SET pontos_disponiveis = pontos_disponiveis + %s 
            WHERE id = %s
        """
        Database.execute_query(query, (int(quantidade), user_id), fetch=False)
        return True
    
    @staticmethod
    def remover_pontos(user_id, quantidade):
        """Remove pontos de um usuário (não permite valores negativos)"""
        query = """
            UPDATE usuarios 
            SET pontos_disponiveis = GREATEST(0, pontos_disponiveis - %s) 
            WHERE id = %s
        """
        Database.execute_query(query, (int(quantidade), user_id), fetch=False)
        return True
    
    @staticmethod
    def definir_pontos(user_id, quantidade):
        """Define a quantidade exata de pontos de um usuário"""
        query = "UPDATE usuarios SET pontos_disponiveis = %s WHERE id = %s"
        Database.execute_query(query, (max(0, int(quantidade)), user_id), fetch=False)
        return True
    
    @staticmethod
    def get_pontos_disponiveis(user_id):
        """Retorna a quantidade de pontos disponíveis de um usuário"""
        query = "SELECT pontos_disponiveis FROM usuarios WHERE id = %s"
        result = Database.execute_query(query, (user_id,))
        return result[0]['pontos_disponiveis'] if result else 0

