from flask import Flask, render_template, request, redirect
app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/home', methods = ['post'])
def home():
    return render_template('home.html')

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

@app.route('user')
def user():
    return render_template('user.html')