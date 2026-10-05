from flask import Blueprint

bp = Blueprint('admin', __name__)

from routes.admin import gestao, origens  # noqa: E402, F401
