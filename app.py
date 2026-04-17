from flask import Flask, render_template, request, redirect
app = Flask(__name__)

@app.route('/')
def cadastro():
    return render_template('login.html')

@app.route('/home', methods = ['post'])
def home():
    return render_template('home.html')