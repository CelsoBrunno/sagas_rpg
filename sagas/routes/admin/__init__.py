from flask import Blueprint

bp = Blueprint('admin', __name__)

from routes.admin import catalogo, gestao, origens  # noqa: E402, F401
