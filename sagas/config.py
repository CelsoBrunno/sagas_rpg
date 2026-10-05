# ==========================================
# Sistema de Campanha GURPS - Configurações
# ==========================================

import os
from dotenv import load_dotenv

# Caminho explícito: no servidor web a pasta atual não é a do projeto
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

class Config:
    """Configurações principais da aplicação"""
    
    # Configurações do Flask.
    # Sem SECRET_KEY no ambiente, a chave fraca só existe com DEBUG=true.
    # O app web recusa subir no outro caso (veja app.py).
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.environ.get('SECRET_KEY') or (
        'dev-secret-key-change-in-production' if DEBUG else ''
    )
    
    # Credenciais ficam no .env. Não grave senha neste arquivo.
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'sagas_gurps'
    
    # Configurações de cálculo GURPS 
    MULTIPLICADOR_VELOCIDADE_BASICA = 4  # (DX + HT) / 4
    ESQUIVA_BASE = 3  # Esquiva base = Velocidade Básica + 3
    APARAR_BASE = 3  # Aparar base = NH/2 + 3
    BLOQUEIO_BASE = 5  # Bloqueio com escudo = HT/2 + 5

