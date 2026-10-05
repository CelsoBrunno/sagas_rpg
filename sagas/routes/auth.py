# Login, logout e cadastro

from flask import flash, redirect, render_template, request, session, url_for
from models import Usuario
from flask import Blueprint

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        usuario = Usuario.buscar_por_username(username)
        
        if usuario and Usuario.verificar_senha(usuario['hashed_password'], password):
            if Usuario.senha_legado(usuario['hashed_password']):
                Usuario.definir_senha(usuario['id'], password)
            session['user_id'] = usuario['id']
            session['username'] = usuario['username']
            session['role'] = usuario['role']
            
            Usuario.atualizar_last_login(usuario['id'])
            
            flash(f'Bem-vindo, {usuario["username"]}!', 'success')
            return redirect(url_for('campanhas.listar_campanhas'))
        else:
            flash('Usuário ou senha incorretos.', 'danger')
    
    return render_template('login.html')

@bp.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de novos usuários"""
    if request.method == 'POST':
        dados = {
            'username': request.form.get('username'),
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'nome_completo': request.form.get('nome_completo'),
            'role': 'usuario'  # Novos usuários são sempre 'usuario'
        }
        
        try:
            Usuario.criar(dados)
            flash('Usuário criado com sucesso! Faça login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Erro ao criar usuário: {str(e)}', 'danger')
    
    return render_template('register.html')
