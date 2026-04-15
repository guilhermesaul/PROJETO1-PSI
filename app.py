from flask import Flask, render_template, request, redirect
app = Flask(__name__)

@app.route('/')
def cadastro():
    return render_template('cadastro.html')

@app.route('/home')
def home():
    return render_template('home.html')