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

        quantidade = conexao.execute('SELECT COUNT(*) FROM usuarios').fetchone()[0]
        if quantidade == 0:
            conexao.executemany(
                'INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)',
                [
                    ('Guilherme', 'gui@devspace.com', '123456'),
                    ('Ana Silva', 'ana@devspace.com', '1234')
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


inicializar_banco()