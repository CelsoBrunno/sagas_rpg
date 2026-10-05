# ==========================================
# Sistema de Campanha GURPS - Flask App
# ==========================================

import os

from flask import Flask, jsonify, session

from config import Config
from database import Database
from models.campanha import Campanha
from utils.acesso import campanha_da_sessao

if not os.environ.get('SECRET_KEY') and not Config.DEBUG:
    raise RuntimeError(
        'Defina SECRET_KEY no .env. A chave padrão só vale com DEBUG=true.'
    )

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

Database.init_app(app)

from routes.admin import bp as admin_bp
from routes.auth import bp as auth_bp
from routes.bestiario import bp as bestiario_bp
from routes.campanhas import bp as campanhas_bp
from routes.dono_ficha import bp as dono_ficha_bp
from routes.ficha import bp as ficha_bp
from routes.imagens import bp as imagens_bp
from routes.inventario import bp as inventario_bp
from routes.magias import bp as magias_bp
from routes.mundo import bp as mundo_bp
from routes.retratos import bp as retratos_bp

app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(bestiario_bp)
app.register_blueprint(campanhas_bp)
app.register_blueprint(dono_ficha_bp)
app.register_blueprint(ficha_bp)
app.register_blueprint(imagens_bp)
app.register_blueprint(inventario_bp)
app.register_blueprint(magias_bp)
app.register_blueprint(mundo_bp)
app.register_blueprint(retratos_bp)


@app.route('/health')
def health():
    """Verifica o status da aplicação"""
    return jsonify({
        'status': 'healthy',
        'database': 'connected' if Database._connection_pool else 'not_connected'
    })


@app.context_processor
def injetar_campanha_ativa():
    if not session.get('user_id'):
        return {'campanha_ativa': None, 'tema_ativo': 'padrao'}
    campanha = campanha_da_sessao()
    tema = (campanha or {}).get('tema') or 'padrao'
    if tema not in Campanha.TEMAS:
        tema = 'padrao'
    return {'campanha_ativa': campanha, 'tema_ativo': tema}


@app.after_request
def after_request(response):
    """Adiciona headers anti-cache em todas as respostas em modo debug"""
    if Config.DEBUG:
        # Em modo debug, sempre força recarregamento
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response


if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000, use_reloader=True)
