from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = 'devspace-secret-key'

usuarios = {
    'gui@devspace.com': {
        'nome': 'Guilherme',
        'email': 'gui@devspace.com',
        'senha': '123456'
    },
    'ana@devspace.com': {
        'nome': 'Ana Silva',
        'email': 'ana@devspace.com',
        'senha': '1234'
    }
}


def usuario_da_query():
    usuario = session.get('usuario')
    if usuario:
        return usuario

    return {'nome': 'Visitante', 'email': ''}


def listar_usuarios(filtro=''):
    termo = filtro.strip().lower()
    lista = []

    for email, dados in usuarios.items():
        if not termo or termo in dados['nome'].lower() or termo in email.lower():
            lista.append({
                'nome': dados['nome'],
                'email': email,
                'senha': dados['senha']
            })

    return sorted(lista, key=lambda item: item['nome'].lower())


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '').strip()
        usuario = usuarios.get(email)

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

        if email in usuarios:
            flash('Esse e-mail já está cadastrado.')
            return redirect(url_for('cadastro'))

        usuarios[email] = {
            'nome': nome,
            'email': email,
            'senha': senha
        }

        flash('Cadastro realizado com sucesso. Faça login para continuar.')
        return redirect(url_for('login'))

    return render_template('cadastro.html')

@app.route('/home')
def home():
    usuario = usuario_da_query()
    return render_template('home.html', usuario=usuario)

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route('/user')
def user_page():
    usuario = usuario_da_query()
    buscar = request.args.get('buscar', '').strip()
    email_visualizado = request.args.get('visualizar', '').strip().lower()
    email_edicao = request.args.get('editar', '').strip().lower()

    return render_template(
        'user.html',
        usuario=usuario,
        buscar=buscar,
        usuarios_filtrados=listar_usuarios(buscar),
        usuario_selecionado=usuarios.get(email_visualizado),
        email_selecionado=email_visualizado,
        usuario_edicao=usuarios.get(email_edicao),
        email_edicao=email_edicao,
        erro_usuario=request.args.get('erro', '')
    )


@app.route('/user/salvar', methods=['POST'])
def salvar_usuario():
    usuario = usuario_da_query()
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

    if email in usuarios:
        flash('Esse e-mail já está cadastrado.')
        return redirect(url_for('user_page', buscar=buscar))

    usuarios[email] = {
        'nome': nome,
        'email': email,
        'senha': senha
    }

    return redirect(url_for('mostrar_usuario', email_usuario=email))


@app.route('/user/<email_usuario>')
def mostrar_usuario(email_usuario):
    usuario = usuario_da_query()
    registro = usuarios.get(email_usuario.strip().lower())

    if not registro:
        flash('Usuário não encontrado.')
        return redirect(url_for('user_page'))

    return render_template(
        'user.html',
        usuario=usuario,
        buscar='',
        usuarios_filtrados=listar_usuarios(),
        usuario_selecionado=registro,
        email_selecionado=registro['email'],
        usuario_edicao=None,
        erro_usuario=''
    )


@app.route('/user/editar/<email_usuario>', methods=['GET', 'POST'])
def editar_usuario(email_usuario):
    usuario = usuario_da_query()
    email_usuario = email_usuario.strip().lower()
    registro = usuarios.get(email_usuario)

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

        if email_novo != email_usuario and email_novo in usuarios:
            flash('Esse e-mail já está cadastrado.')
            return redirect(url_for('editar_usuario', email_usuario=email_usuario, buscar=buscar))

        if email_novo != email_usuario:
            del usuarios[email_usuario]

        usuarios[email_novo] = {
            'nome': nome,
            'email': email_novo,
            'senha': senha
        }

        return redirect(url_for('mostrar_usuario', email_usuario=email_novo))

    return render_template(
        'user.html',
        usuario=usuario,
        buscar=request.args.get('buscar', '').strip(),
        usuarios_filtrados=listar_usuarios(request.args.get('buscar', '')),
        usuario_selecionado=registro,
        email_selecionado=email_usuario,
        usuario_edicao=registro,
        erro_usuario=''
    )


@app.route('/user/remover/<email_usuario>', methods=['POST'])
def remover_usuario(email_usuario):
    usuario = usuario_da_query()
    email_usuario = email_usuario.strip().lower()

    if email_usuario in usuarios:
        del usuarios[email_usuario]

    return redirect(url_for('user_page'))


@app.route('/cursos/html5')
def html5():
    return render_template('cursos/html5.html')

@app.route('/cursos/javascript')
def javascript():
    return render_template('cursos/javascript.html')

@app.route('/cursos/python')
def python():
    return render_template('cursos/python.html')

@app.route('/cursos/mysql')
def mysql():
    return render_template('cursos/mysql.html')