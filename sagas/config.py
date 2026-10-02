# ==========================================
# Sistema de Campanha GURPS - Configurações
# ==========================================

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configurações principais da aplicação"""
    
    # Configurações do Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Credenciais ficam no .env. Não grave senha neste arquivo.
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'sagas_gurps'
    
    # Configurações gerais
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Configurações de cálculo GURPS 
    MULTIPLICADOR_VELOCIDADE_BASICA = 4  # (DX + HT) / 4
    ESQUIVA_BASE = 3  # Esquiva base = Velocidade Básica + 3
    APARAR_BASE = 3  # Aparar base = NH/2 + 3
    BLOQUEIO_BASE = 5  # Bloqueio com escudo = HT/2 + 5

