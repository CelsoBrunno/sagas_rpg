from flask import Blueprint

bp = Blueprint('ficha', __name__)

from routes.ficha import paginas, api  # noqa: E402, F401
