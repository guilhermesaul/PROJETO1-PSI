# DevSpace — Plataforma de Cursos de Programação

Aplicação web desenvolvida com **Flask** e **SQLite3** para gerenciamento de uma plataforma de cursos online.

## 🚀 Como executar o projeto

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/SEU_USUARIO/PROJETO1-PSI.git
cd PROJETO1-PSI
```

2. (Opcional) Crie e ative um ambiente virtual:
```bash
python -m venv env
# Windows:
env\Scripts\activate
# Linux/Mac:
source env/bin/activate
```

3. Instale as dependências:
```bash
pip install flask
```

4. Execute a aplicação:
```bash
python app.py
```

5. Acesse no navegador: [http://localhost:5000](http://localhost:5000)

---

## 📁 Estrutura do Projeto

```
PROJETO1-PSI/
├── app.py              # Aplicação Flask principal (rotas)
├── db.py               # Módulo de banco de dados SQLite3
├── usuarios.db         # Arquivo do banco de dados
├── templates/          # Templates HTML (Jinja2)
│   ├── base.html       # Template base com header e footer
│   ├── base-forms.html # Template base para formulários de auth
│   ├── login.html      # Página de login
│   ├── cadastro.html   # Página de cadastro de usuário
│   ├── home.html       # Página inicial (área logada)
│   ├── user.html       # Gerenciamento de usuários (CRUD)
│   └── cursos/
│       ├── gerenciar.html  # Gerenciamento de cursos (CRUD)
│       ├── html5.html
│       ├── javascript.html
│       ├── python.html
│       └── mysql.html
└── static/             # Arquivos estáticos
    ├── css/            # Folhas de estilo
    ├── js/             # Scripts JavaScript
    └── imgs/           # Imagens e ícones
```

## 🔐 Usuários de teste

| E-mail                | Senha  |
|-----------------------|--------|
| gui@devspace.com      | 123456 |
| ana@devspace.com      | 1234   |

## 🗄️ Banco de Dados

O banco `usuarios.db` é criado automaticamente na primeira execução com as tabelas:
- **usuarios** — armazena os dados de autenticação dos usuários
- **cursos** — armazena os cursos da plataforma (entidade principal do CRUD)

## ✨ Funcionalidades

- Cadastro, login e logout de usuários
- Controle de sessão com `session` do Flask
- CRUD completo de usuários (listar, mostrar, editar, remover)
- CRUD completo de cursos (cadastrar, listar, mostrar, editar, remover)
- Busca e filtragem por string de consulta (`?buscar=`)
- Rotas parametrizadas (`/gerenciar-cursos/<id>`)
- Diferenciação visual entre área pública e área logada
- Proteção de rotas — apenas usuários autenticados acessam o sistema