# ==========================================
# Sistema de Campanha GURPS - Database
# ==========================================

import mysql.connector
from mysql.connector import pooling
from config import Config

class Database:
    """Gerenciador de conexão com o banco de dados MySQL"""
    
    _connection_pool = None
    
    @staticmethod
    def init_app(app, pool_size=5):
        """Inicializa o pool de conexões
        
        Args:
            app: Instância Flask (pode ser None para scripts)
            pool_size: Tamanho do pool de conexões (padrão: 5)
                      Use 1 para scripts no PythonAnywhere devido ao limite de conexões
        """
        try:
            Database._connection_pool = pooling.MySQLConnectionPool(
                pool_name="sagas_pool",
                pool_size=pool_size,
                pool_reset_session=True,
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DB,
                autocommit=False
            )
            pass  # Pool inicializado com sucesso
        except mysql.connector.Error as err:
            raise RuntimeError(f"Erro ao criar pool de conexões: {err}")
    
    @staticmethod
    def get_connection():
        """Obtém uma conexão do pool"""
        if Database._connection_pool is None:
            raise RuntimeError("Pool de conexões não foi inicializado. Chame init_app() primeiro.")
        
        try:
            return Database._connection_pool.get_connection()
        except mysql.connector.Error as err:
            raise RuntimeError(f"Erro ao obter conexão: {err}")
    
    @staticmethod
    def execute_query(query, params=None, fetch=True):
        """Executa uma query e retorna os resultados"""
        connection = None
        cursor = None
        
        try:
            connection = Database.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                result = cursor.fetchall()
                connection.commit()
                return result
            else:
                connection.commit()
                return cursor.lastrowid
                
        except mysql.connector.Error as err:
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

