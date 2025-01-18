from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'seu_seguro_chave_secreta'

# Dados de login estáticos para exemplo
users = {'admin': 'password'}

# Lista de logs e máquinas ativas
logs = []
active_machines = ['Machine1', 'Machine2', 'Machine3']
log_file = 'logs.txt'

def read_logs():
    """Lê os logs do arquivo logs.txt."""
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            return file.readlines()
    return []

def write_log(log_entry):
    """Escreve um novo log no arquivo logs.txt."""
    with open(log_file, 'a') as file:
        file.write(log_entry + '\n')

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('c2'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('c2'))
        return "Invalid credentials, please try again."
    return render_template('login.html')

@app.route('/c2', methods=['GET', 'POST'])
def c2():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        machine = request.form['machine']
        command = request.form['command']
        log_entry = f"{machine}: {command} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        write_log(log_entry)
        logs.append(log_entry)
        return redirect(url_for('c2'))
    
    logs.clear()
    logs.extend(read_logs())
    return render_template('c2.html', logs=logs, machines=active_machines)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5010)