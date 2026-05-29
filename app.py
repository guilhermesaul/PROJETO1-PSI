from flask import Flask, flash, redirect, render_template, request, session, url_for
from functools import wraps
from db import atualizar_usuario, buscar_usuario_por_email, inserir_usuario, listar_usuarios, remover_usuario as remover_usuario_banco


app = Flask(__name__)
app.secret_key = 'devspace-secret-key'


def login_requerido(f):
    @wraps(f)
    def verificar(*args, **kwargs):
        if not session.get('usuario'):
            flash('você precisa estar logado para acessar essa página.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return verificar


def usuario_da_query():
    usuario = session.get('usuario')
    if usuario:
        return usuario

    return {'nome': 'Visitante', 'email': ''}


@app.route('/', methods=['GET', 'POST'])
def login():
    if session.get('usuario'):
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '').strip()
        usuario = buscar_usuario_por_email(email)

        if not email or not senha:
            flash('Preencha e-mail e senha.')
            return redirect(url_for('login'))

        if not usuario:
            flash('Esse e-mail não está cadastrado.')
            return redirect(url_for('login'))

        if len(senha) < 4:
            flash('A senha precisa ter no mínimo 4 caracteres.')
            return redirect(url_for('login'))

        if usuario['senha'] != senha:
            flash('Senha incorreta.')
            return redirect(url_for('login'))

        session['usuario'] = {
            'nome': usuario['nome'],
            'email': usuario['email']
        }

        return redirect(url_for('home'))

    return render_template('login.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if session.get('usuario'):
        return redirect(url_for('home'))
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '').strip()

        if not nome or not email or not senha:
            flash('Preencha todos os campos.')
            return redirect(url_for('cadastro'))

        if len(senha) < 4:
            flash('A senha precisa ter no mínimo 4 caracteres.')
            return redirect(url_for('cadastro'))

        if buscar_usuario_por_email(email):
            flash('Esse e-mail já está cadastrado.')
            return redirect(url_for('cadastro'))

        inserir_usuario(nome, email, senha)

        flash('Cadastro realizado com sucesso. Faça login para continuar.')
        return redirect(url_for('login'))

    return render_template('cadastro.html')


@app.route('/home')
@login_requerido
def home():
    usuario = usuario_da_query()
    return render_template('home.html', usuario=usuario)


@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))


@app.route('/user')
@login_requerido
def user_page():
    usuario = usuario_da_query()
    buscar = request.args.get('buscar', '').strip()
    ordem  = request.args.get('ordem', 'nome')
    email_visualizado = request.args.get('visualizar', '').strip().lower()
    email_edicao = request.args.get('editar', '').strip().lower()
       
    usuarios_filtrados = listar_usuarios(buscar)

    if ordem == 'email':                                    # ← adicionar
     usuarios_filtrados = sorted(
        usuarios_filtrados, key=lambda u: u['email'].lower()
    )

    return render_template(
        'user.html',
        usuario=usuario,
        buscar=buscar,
        ordem =ordem,
        usuarios_filtrados=usuarios_filtrados,
        usuario_selecionado=buscar_usuario_por_email(email_visualizado),
        email_selecionado=email_visualizado,
        usuario_edicao=buscar_usuario_por_email(email_edicao),
        email_edicao=email_edicao,
        erro_usuario=request.args.get('erro', '')
    )


@app.route('/user/salvar', methods=['POST'])
@login_requerido
def salvar_usuario():
    nome = request.form.get('nome', '').strip()
    email = request.form.get('email', '').strip().lower()
    senha = request.form.get('senha', '').strip()
    buscar = request.args.get('buscar', '').strip()

    if not nome or not email or not senha:
        flash('Preencha nome, e-mail e senha.')
        return redirect(url_for('user_page', buscar=buscar))

    if len(senha) < 4:
        flash('A senha precisa ter no mínimo 4 caracteres.')
        return redirect(url_for('user_page', buscar=buscar))

    if buscar_usuario_por_email(email):
        flash('Esse e-mail já está cadastrado.')
        return redirect(url_for('user_page', buscar=buscar))

    inserir_usuario(nome, email, senha)
    flash('Usuário cadastrado com sucesso.')

    return redirect(url_for('mostrar_usuario', email_usuario=email))


@app.route('/user/<email_usuario>')
@login_requerido
def mostrar_usuario(email_usuario):
    usuario = usuario_da_query()
    registro = buscar_usuario_por_email(email_usuario.strip().lower())

    if not registro:
        flash('Usuário não encontrado.')
        return redirect(url_for('user_page'))

    return render_template(
        'user.html',
        usuario=usuario,
        buscar='',
        ordem='nome',
        usuarios_filtrados=listar_usuarios(),
        usuario_selecionado=registro,
        email_selecionado=registro['email'],
        usuario_edicao=None,
        erro_usuario=''
    )


@app.route('/user/editar/<email_usuario>', methods=['GET', 'POST'])
@login_requerido
def editar_usuario(email_usuario):
    usuario = usuario_da_query()
    email_usuario = email_usuario.strip().lower()
    registro = buscar_usuario_por_email(email_usuario)

    if not registro:
        flash('Usuário não encontrado.')
        return redirect(url_for('user_page'))

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email_novo = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '').strip()
        buscar = request.args.get('buscar', '').strip()

        if not nome or not email_novo or not senha:
            flash('Preencha todos os campos para editar.')
            return redirect(url_for('editar_usuario', email_usuario=email_usuario, buscar=buscar))

        if len(senha) < 4:
            flash('A senha precisa ter no mínimo 4 caracteres.')
            return redirect(url_for('editar_usuario', email_usuario=email_usuario, buscar=buscar))

        if email_novo != email_usuario and buscar_usuario_por_email(email_novo):
            flash('Esse e-mail já está cadastrado.')
            return redirect(url_for('editar_usuario', email_usuario=email_usuario, buscar=buscar))

        atualizar_usuario(email_usuario, nome, email_novo, senha)
        flash('Usuário atualizado com sucesso.') 

        if session.get('usuario', {}).get('email', '').lower() == email_usuario:
            session['usuario'] = {
                'nome': nome,
                'email': email_novo
            }

        return redirect(url_for('mostrar_usuario', email_usuario=email_novo))

    return render_template(
        'user.html',
        usuario=usuario,
        buscar=request.args.get('buscar', '').strip(),
        ordem='nome',
        usuarios_filtrados=listar_usuarios(request.args.get('buscar', '')),
        usuario_selecionado=registro,
        email_selecionado=email_usuario,
        usuario_edicao=registro,
        erro_usuario=''
    )


@app.route('/user/remover/<email_usuario>', methods=['POST'])
@login_requerido
def remover_usuario(email_usuario):
    email_usuario = email_usuario.strip().lower()

    if buscar_usuario_por_email(email_usuario):
        remover_usuario_banco(email_usuario)
        flash('Usuário removido.')

        if session.get('usuario', {}).get('email', '').lower() == email_usuario:
            session.pop('usuario', None)
            
            return redirect(url_for('login')) 
    return redirect(url_for('user_page'))


@app.route('/cursos/html5')
@login_requerido
def html5():
    return render_template('cursos/html5.html')


@app.route('/cursos/javascript')
@login_requerido
def javascript():
    return render_template('cursos/javascript.html')


@app.route('/cursos/python')
@login_requerido
def python():
    return render_template('cursos/python.html')


@app.route('/cursos/mysql')
@login_requerido
def mysql():
    return render_template('cursos/mysql.html')