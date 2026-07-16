from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


# ── MODELO 1: User ────────────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    senha_hash = db.Column(db.String(256), nullable=False)

    # Relacionamento: um usuário pode ter várias matrículas
    matriculas = db.relationship('Matricula', back_populates='usuario',
                                 cascade='all, delete-orphan', lazy='dynamic')

    def set_password(self, senha):
        """Gera e armazena o hash da senha."""
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        """Verifica se a senha fornecida corresponde ao hash armazenado."""
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f'<User {self.email}>'


# ── MODELO 2: Curso ───────────────────────────────────────────────────────────
class Curso(db.Model):
    __tablename__ = 'cursos'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    instrutor = db.Column(db.String(120), nullable=False)
    categoria = db.Column(db.String(80), nullable=False)
    carga_horaria = db.Column(db.Integer, nullable=False)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text, default='')

    # Relacionamento: um curso pode ter várias matrículas
    matriculas = db.relationship('Matricula', back_populates='curso',
                                 cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<Curso {self.titulo}>'


# ── MODELO 3: Matricula (chave estrangeira para User e Curso) ─────────────────
class Matricula(db.Model):
    __tablename__ = 'matriculas'

    id = db.Column(db.Integer, primary_key=True)

    # Chave estrangeira → User
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    # Chave estrangeira → Curso
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)

    data_matricula = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relacionamentos inversos
    usuario = db.relationship('User', back_populates='matriculas')
    curso = db.relationship('Curso', back_populates='matriculas')

    # Garante que um usuário não se matricule duas vezes no mesmo curso
    __table_args__ = (
        db.UniqueConstraint('user_id', 'curso_id', name='uq_user_curso'),
    )

    def __repr__(self):
        return f'<Matricula user={self.user_id} curso={self.curso_id}>'
