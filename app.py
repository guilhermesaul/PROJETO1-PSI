from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)

from models import Curso, Matricula, User, db


# ── CONFIGURAÇÃO DA APLICAÇÃO ─────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'devspace-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa SQLAlchemy com a app
db.init_app(app)

# ── FLASK-LOGIN ───────────────────────────────────────────────────────────────
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Você precisa estar logado para acessar essa página.'


@login_manager.user_loader
def carregar_usuario(user_id):
    return db.session.get(User, int(user_id))


# ── INICIALIZAÇÃO DO BANCO ────────────────────────────────────────────────────
def seed_banco():
    """Popula o banco com dados iniciais se estiver vazio."""
    if User.query.count() == 0:
        u1 = User(nome='Guilherme', email='gui@devspace.com')
        u1.set_password('123456')
        u2 = User(nome='Ana Silva', email='ana@devspace.com')
        u2.set_password('1234')
        db.session.add_all([u1, u2])

    if Curso.query.count() == 0:
        cursos_iniciais = [
            Curso(titulo='HTML 5', instrutor='Ana Silva', categoria='Front-end',
                  carga_horaria=40, preco=89.90,
                  descricao='Aprenda HTML do zero ao avançado com projetos práticos.'),
            Curso(titulo='JavaScript do Sênior ao Júnior', instrutor='Romerito',
                  categoria='Back-end', carga_horaria=60, preco=129.90,
                  descricao='Domine JavaScript moderno com ES6+, async/await e muito mais.'),
            Curso(titulo='Python com Flask', instrutor='Thales',
                  categoria='Back-end', carga_horaria=50, preco=99.90,
                  descricao='Construa aplicações web completas com Python e Flask.'),
            Curso(titulo='SQL para Iniciantes', instrutor='Maria José',
                  categoria='Banco de Dados', carga_horaria=30, preco=69.90,
                  descricao='Aprenda consultas SQL do básico ao intermediário.'),
        ]
        db.session.add_all(cursos_iniciais)

    db.session.commit()


# ── AUTENTICAÇÃO ──────────────────────────────────────────────────────────────
@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '').strip()

        if not email or not senha:
            flash('Preencha e-mail e senha.')
            return redirect(url_for('login'))

        usuario = User.query.filter_by(email=email).first()

        if not usuario:
            flash('Esse e-mail não está cadastrado.')
            return redirect(url_for('login'))

        if not usuario.check_password(senha):
            flash('Senha incorreta.')
            return redirect(url_for('login'))

        login_user(usuario)
        return redirect(url_for('home'))

    return render_template('login.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
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

        if User.query.filter_by(email=email).first():
            flash('Esse e-mail já está cadastrado.')
            return redirect(url_for('cadastro'))

        novo = User(nome=nome, email=email)
        novo.set_password(senha)
        db.session.add(novo)
        db.session.commit()

        flash('Cadastro realizado com sucesso. Faça login para continuar.')
        return redirect(url_for('login'))

    return render_template('cadastro.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ── HOME ──────────────────────────────────────────────────────────────────────
@app.route('/home')
@login_required
def home():
    return render_template('home.html')


# ── CRUD USUÁRIOS ─────────────────────────────────────────────────────────────
@app.route('/user')
@login_required
def user_page():
    buscar = request.args.get('buscar', '').strip()
    ordem = request.args.get('ordem', 'nome')

    query = User.query
    if buscar:
        termo = f'%{buscar.lower()}%'
        query = query.filter(
            db.or_(User.nome.ilike(termo), User.email.ilike(termo))
        )

    if ordem == 'email':
        usuarios_filtrados = query.order_by(User.email).all()
    else:
        usuarios_filtrados = query.order_by(User.nome).all()

    email_visualizado = request.args.get('visualizar', '').strip().lower()
    email_edicao = request.args.get('editar', '').strip().lower()

    return render_template(
        'user.html',
        buscar=buscar,
        ordem=ordem,
        usuarios_filtrados=usuarios_filtrados,
        usuario_selecionado=User.query.filter_by(email=email_visualizado).first() if email_visualizado else None,
        email_selecionado=email_visualizado,
        usuario_edicao=User.query.filter_by(email=email_edicao).first() if email_edicao else None,
        email_edicao=email_edicao,
        erro_usuario=request.args.get('erro', '')
    )


@app.route('/user/salvar', methods=['POST'])
@login_required
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

    if User.query.filter_by(email=email).first():
        flash('Esse e-mail já está cadastrado.')
        return redirect(url_for('user_page', buscar=buscar))

    novo = User(nome=nome, email=email)
    novo.set_password(senha)
    db.session.add(novo)
    db.session.commit()

    flash('Usuário cadastrado com sucesso.')
    return redirect(url_for('mostrar_usuario', email_usuario=email))


@app.route('/user/<email_usuario>')
@login_required
def mostrar_usuario(email_usuario):
    registro = User.query.filter_by(email=email_usuario.strip().lower()).first()

    if not registro:
        flash('Usuário não encontrado.')
        return redirect(url_for('user_page'))

    return render_template(
        'user.html',
        buscar='',
        ordem='nome',
        usuarios_filtrados=User.query.order_by(User.nome).all(),
        usuario_selecionado=registro,
        email_selecionado=registro.email,
        usuario_edicao=None,
        erro_usuario=''
    )


@app.route('/user/editar/<email_usuario>', methods=['GET', 'POST'])
@login_required
def editar_usuario(email_usuario):
    email_usuario = email_usuario.strip().lower()
    registro = User.query.filter_by(email=email_usuario).first()

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

        if email_novo != email_usuario and User.query.filter_by(email=email_novo).first():
            flash('Esse e-mail já está cadastrado.')
            return redirect(url_for('editar_usuario', email_usuario=email_usuario, buscar=buscar))

        registro.nome = nome
        registro.email = email_novo
        registro.set_password(senha)
        db.session.commit()

        flash('Usuário atualizado com sucesso.')
        return redirect(url_for('mostrar_usuario', email_usuario=email_novo))

    return render_template(
        'user.html',
        buscar=request.args.get('buscar', '').strip(),
        ordem='nome',
        usuarios_filtrados=User.query.order_by(User.nome).all(),
        usuario_selecionado=registro,
        email_selecionado=email_usuario,
        usuario_edicao=registro,
        erro_usuario=''
    )


@app.route('/user/remover/<email_usuario>', methods=['POST'])
@login_required
def remover_usuario(email_usuario):
    email_usuario = email_usuario.strip().lower()
    registro = User.query.filter_by(email=email_usuario).first()

    if registro:
        era_eu = (current_user.email == email_usuario)
        db.session.delete(registro)
        db.session.commit()
        flash('Usuário removido.')

        if era_eu:
            logout_user()
            return redirect(url_for('login'))

    return redirect(url_for('user_page'))


# ── PÁGINAS DE CURSOS (visualização) ─────────────────────────────────────────
@app.route('/cursos/html5')
@login_required
def html5():
    return render_template('cursos/html5.html')


@app.route('/cursos/javascript')
@login_required
def javascript():
    return render_template('cursos/javascript.html')


@app.route('/cursos/python')
@login_required
def python():
    return render_template('cursos/python.html')


@app.route('/cursos/mysql')
@login_required
def mysql():
    return render_template('cursos/mysql.html')


# ── CRUD CURSOS ───────────────────────────────────────────────────────────────
@app.route('/gerenciar-cursos')
@login_required
def gerenciar_cursos():
    buscar = request.args.get('buscar', '').strip()

    query = Curso.query
    if buscar:
        termo = f'%{buscar.lower()}%'
        query = query.filter(
            db.or_(
                Curso.titulo.ilike(termo),
                Curso.categoria.ilike(termo),
                Curso.instrutor.ilike(termo)
            )
        )

    cursos = query.order_by(Curso.titulo).all()

    return render_template(
        'cursos/gerenciar.html',
        cursos=cursos,
        buscar=buscar,
        curso_selecionado=None,
        curso_edicao=None
    )


@app.route('/gerenciar-cursos/salvar', methods=['POST'])
@login_required
def salvar_curso():
    titulo = request.form.get('titulo', '').strip()
    instrutor = request.form.get('instrutor', '').strip()
    categoria = request.form.get('categoria', '').strip()
    carga_horaria = request.form.get('carga_horaria', '').strip()
    preco = request.form.get('preco', '').strip()
    descricao = request.form.get('descricao', '').strip()

    if not titulo or not instrutor or not categoria or not carga_horaria or not preco:
        flash('Preencha todos os campos obrigatórios.')
        return redirect(url_for('gerenciar_cursos'))

    novo = Curso(titulo=titulo, instrutor=instrutor, categoria=categoria,
                 carga_horaria=int(carga_horaria), preco=float(preco),
                 descricao=descricao)
    db.session.add(novo)
    db.session.commit()

    flash('Curso cadastrado com sucesso!')
    return redirect(url_for('gerenciar_cursos'))


@app.route('/gerenciar-cursos/<int:id_curso>')
@login_required
def mostrar_curso(id_curso):
    curso = db.session.get(Curso, id_curso)

    if not curso:
        flash('Curso não encontrado.')
        return redirect(url_for('gerenciar_cursos'))

    return render_template(
        'cursos/gerenciar.html',
        cursos=Curso.query.order_by(Curso.titulo).all(),
        buscar='',
        curso_selecionado=curso,
        curso_edicao=None
    )


@app.route('/gerenciar-cursos/editar/<int:id_curso>', methods=['GET', 'POST'])
@login_required
def editar_curso(id_curso):
    curso = db.session.get(Curso, id_curso)

    if not curso:
        flash('Curso não encontrado.')
        return redirect(url_for('gerenciar_cursos'))

    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        instrutor = request.form.get('instrutor', '').strip()
        categoria = request.form.get('categoria', '').strip()
        carga_horaria = request.form.get('carga_horaria', '').strip()
        preco = request.form.get('preco', '').strip()
        descricao = request.form.get('descricao', '').strip()

        if not titulo or not instrutor or not categoria or not carga_horaria or not preco:
            flash('Preencha todos os campos obrigatórios.')
            return redirect(url_for('editar_curso', id_curso=id_curso))

        curso.titulo = titulo
        curso.instrutor = instrutor
        curso.categoria = categoria
        curso.carga_horaria = int(carga_horaria)
        curso.preco = float(preco)
        curso.descricao = descricao
        db.session.commit()

        flash('Curso atualizado com sucesso!')
        return redirect(url_for('mostrar_curso', id_curso=id_curso))

    return render_template(
        'cursos/gerenciar.html',
        cursos=Curso.query.order_by(Curso.titulo).all(),
        buscar='',
        curso_selecionado=curso,
        curso_edicao=curso
    )


@app.route('/gerenciar-cursos/remover/<int:id_curso>', methods=['POST'])
@login_required
def remover_curso(id_curso):
    curso = db.session.get(Curso, id_curso)
    if curso:
        db.session.delete(curso)
        db.session.commit()
        flash('Curso removido com sucesso.')
    return redirect(url_for('gerenciar_cursos'))


# ── CRUD MATRÍCULAS ───────────────────────────────────────────────────────────
@app.route('/matriculas')
@login_required
def gerenciar_matriculas():
    buscar = request.args.get('buscar', '').strip()

    query = (
        Matricula.query
        .join(User)
        .join(Curso)
    )

    if buscar:
        termo = f'%{buscar.lower()}%'
        query = query.filter(
            db.or_(
                User.nome.ilike(termo),
                User.email.ilike(termo),
                Curso.titulo.ilike(termo)
            )
        )

    matriculas = query.order_by(Matricula.data_matricula.desc()).all()
    usuarios = User.query.order_by(User.nome).all()
    cursos = Curso.query.order_by(Curso.titulo).all()

    matricula_id = request.args.get('visualizar', type=int)
    matricula_selecionada = db.session.get(Matricula, matricula_id) if matricula_id else None

    return render_template(
        'matriculas/gerenciar.html',
        matriculas=matriculas,
        usuarios=usuarios,
        cursos=cursos,
        buscar=buscar,
        matricula_selecionada=matricula_selecionada
    )


@app.route('/matriculas/salvar', methods=['POST'])
@login_required
def salvar_matricula():
    user_id = request.form.get('user_id', type=int)
    curso_id = request.form.get('curso_id', type=int)

    if not user_id or not curso_id:
        flash('Selecione um usuário e um curso.')
        return redirect(url_for('gerenciar_matriculas'))

    if not db.session.get(User, user_id) or not db.session.get(Curso, curso_id):
        flash('Usuário ou curso não encontrado.')
        return redirect(url_for('gerenciar_matriculas'))

    ja_existe = Matricula.query.filter_by(user_id=user_id, curso_id=curso_id).first()
    if ja_existe:
        flash('Esse usuário já está matriculado neste curso.')
        return redirect(url_for('gerenciar_matriculas'))

    nova = Matricula(user_id=user_id, curso_id=curso_id)
    db.session.add(nova)
    db.session.commit()

    flash('Matrícula realizada com sucesso!')
    return redirect(url_for('gerenciar_matriculas'))


@app.route('/matriculas/<int:id_matricula>')
@login_required
def mostrar_matricula(id_matricula):
    matricula = db.session.get(Matricula, id_matricula)

    if not matricula:
        flash('Matrícula não encontrada.')
        return redirect(url_for('gerenciar_matriculas'))

    matriculas = Matricula.query.join(User).join(Curso).order_by(Matricula.data_matricula.desc()).all()
    usuarios = User.query.order_by(User.nome).all()
    cursos = Curso.query.order_by(Curso.titulo).all()

    return render_template(
        'matriculas/gerenciar.html',
        matriculas=matriculas,
        usuarios=usuarios,
        cursos=cursos,
        buscar='',
        matricula_selecionada=matricula
    )


@app.route('/matriculas/remover/<int:id_matricula>', methods=['POST'])
@login_required
def remover_matricula(id_matricula):
    matricula = db.session.get(Matricula, id_matricula)
    if matricula:
        db.session.delete(matricula)
        db.session.commit()
        flash('Matrícula cancelada com sucesso.')
    return redirect(url_for('gerenciar_matriculas'))


# ── INICIALIZAÇÃO ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_banco()
    app.run(debug=True)