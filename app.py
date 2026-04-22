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