import os
import sqlite3


BASE_DIR = os.path.dirname(__file__)
CAMINHO_BANCO = os.path.join(BASE_DIR, 'usuarios.db')


def conectar_banco():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def registro_para_usuario(registro):
    if registro is None:
        return None

    return {
        'nome': registro['nome'],
        'email': registro['email'],
        'senha': registro['senha']
    }


def inicializar_banco():
    with conectar_banco() as conexao:
        conexao.execute(
            '''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL
            )
            '''
        )

        conexao.execute(
            '''
            CREATE TABLE IF NOT EXISTS cursos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                instrutor TEXT NOT NULL,
                categoria TEXT NOT NULL,
                carga_horaria INTEGER NOT NULL,
                preco REAL NOT NULL,
                descricao TEXT
            )
            '''
        )

        quantidade = conexao.execute('SELECT COUNT(*) FROM usuarios').fetchone()[0]
        if quantidade == 0:
            conexao.executemany(
                'INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)',
                [
                    ('Guilherme', 'gui@devspace.com', '123456'),
                    ('Ana Silva', 'ana@devspace.com', '1234')
                ]
            )

        qtd_cursos = conexao.execute('SELECT COUNT(*) FROM cursos').fetchone()[0]
        if qtd_cursos == 0:
            conexao.executemany(
                'INSERT INTO cursos (titulo, instrutor, categoria, carga_horaria, preco, descricao) VALUES (?, ?, ?, ?, ?, ?)',
                [
                    ('HTML 5', 'Ana Silva', 'Front-end', 40, 89.90, 'Aprenda HTML do zero ao avançado com projetos práticos.'),
                    ('JavaScript do Sênior ao Júnior', 'Romerito', 'Back-end', 60, 129.90, 'Domine JavaScript moderno com ES6+, async/await e muito mais.'),
                    ('Python com Flask', 'Thales', 'Back-end', 50, 99.90, 'Construa aplicações web completas com Python e Flask.'),
                    ('SQL para Iniciantes', 'Maria José', 'Banco de Dados', 30, 69.90, 'Aprenda consultas SQL do básico ao intermediário.')
                ]
            )


def buscar_usuario_por_email(email):
    with conectar_banco() as conexao:
        registro = conexao.execute(
            'SELECT nome, email, senha FROM usuarios WHERE lower(email) = lower(?)',
            (email,)
        ).fetchone()

    return registro_para_usuario(registro)


def listar_usuarios(filtro=''):
    termo = filtro.strip().lower()

    with conectar_banco() as conexao:
        if termo:
            registros = conexao.execute(
                '''
                SELECT nome, email, senha
                FROM usuarios
                WHERE lower(nome) LIKE ? OR lower(email) LIKE ?
                ORDER BY lower(nome)
                ''',
                (f'%{termo}%', f'%{termo}%')
            ).fetchall()
        else:
            registros = conexao.execute(
                'SELECT nome, email, senha FROM usuarios ORDER BY lower(nome)'
            ).fetchall()

    return [registro_para_usuario(registro) for registro in registros]


def inserir_usuario(nome, email, senha):
    with conectar_banco() as conexao:
        conexao.execute(
            'INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)',
            (nome, email, senha)
        )


def atualizar_usuario(email_atual, nome, email_novo, senha):
    with conectar_banco() as conexao:
        conexao.execute(
            '''
            UPDATE usuarios
            SET nome = ?, email = ?, senha = ?
            WHERE lower(email) = lower(?)
            ''',
            (nome, email_novo, senha, email_atual)
        )


def remover_usuario(email):
    with conectar_banco() as conexao:
        conexao.execute(
            'DELETE FROM usuarios WHERE lower(email) = lower(?)',
            (email,)
        )


# ── CURSOS ────────────────────────────────────────────────

def registro_para_curso(registro):
    if registro is None:
        return None
    return {
        'id': registro['id'],
        'titulo': registro['titulo'],
        'instrutor': registro['instrutor'],
        'categoria': registro['categoria'],
        'carga_horaria': registro['carga_horaria'],
        'preco': registro['preco'],
        'descricao': registro['descricao']
    }


def listar_cursos(filtro=''):
    termo = filtro.strip().lower()
    with conectar_banco() as conexao:
        if termo:
            registros = conexao.execute(
                '''
                SELECT id, titulo, instrutor, categoria, carga_horaria, preco, descricao
                FROM cursos
                WHERE lower(titulo) LIKE ? OR lower(categoria) LIKE ? OR lower(instrutor) LIKE ?
                ORDER BY lower(titulo)
                ''',
                (f'%{termo}%', f'%{termo}%', f'%{termo}%')
            ).fetchall()
        else:
            registros = conexao.execute(
                'SELECT id, titulo, instrutor, categoria, carga_horaria, preco, descricao FROM cursos ORDER BY lower(titulo)'
            ).fetchall()
    return [registro_para_curso(r) for r in registros]


def buscar_curso_por_id(id_curso):
    with conectar_banco() as conexao:
        registro = conexao.execute(
            'SELECT id, titulo, instrutor, categoria, carga_horaria, preco, descricao FROM cursos WHERE id = ?',
            (id_curso,)
        ).fetchone()
    return registro_para_curso(registro)


def inserir_curso(titulo, instrutor, categoria, carga_horaria, preco, descricao):
    with conectar_banco() as conexao:
        conexao.execute(
            'INSERT INTO cursos (titulo, instrutor, categoria, carga_horaria, preco, descricao) VALUES (?, ?, ?, ?, ?, ?)',
            (titulo, instrutor, categoria, carga_horaria, preco, descricao)
        )


def atualizar_curso(id_curso, titulo, instrutor, categoria, carga_horaria, preco, descricao):
    with conectar_banco() as conexao:
        conexao.execute(
            '''
            UPDATE cursos
            SET titulo = ?, instrutor = ?, categoria = ?, carga_horaria = ?, preco = ?, descricao = ?
            WHERE id = ?
            ''',
            (titulo, instrutor, categoria, carga_horaria, preco, descricao, id_curso)
        )


def remover_curso(id_curso):
    with conectar_banco() as conexao:
        conexao.execute('DELETE FROM cursos WHERE id = ?', (id_curso,))


inicializar_banco()