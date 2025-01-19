#!/bin/bash

# Função para exibir a ajuda do script
function usage() {
    echo "Uso: $0 [-p porta]"
    echo "  -p porta   Porta que o servidor Flask está usando"
    exit 1
}

# Lê a porta da linha de comando
while getopts ":p:" opt; do
    case ${opt} in
        p )
            PORT=$OPTARG
            ;;
        \? )
            usage
            ;;
    esac
done

# Verifica se a porta foi fornecida
if [ -z "${PORT}" ]; then
    usage
fi

# Atualizar os pacotes e instalar o Tor
sudo apt update
sudo apt install -y tor

# Configurar o serviço Onion
HIDDEN_SERVICE_DIR="/var/lib/tor/hidden_service/"
TORRC_FILE="/etc/tor/torrc"

# Adicionar configuração do serviço Onion ao torrc, se não existir
if ! grep -q "HiddenServiceDir $HIDDEN_SERVICE_DIR" "$TORRC_FILE"; then
    echo "Adicionando configuração do serviço Onion ao torrc..."
    echo "HiddenServiceDir $HIDDEN_SERVICE_DIR" | sudo tee -a "$TORRC_FILE"
else
    echo "Configuração do serviço Onion já presente no torrc."
fi

# Atualizar a porta no torrc
sudo sed -i "/HiddenServicePort/c\HiddenServicePort 80 127.0.0.1:$PORT" "$TORRC_FILE"

# Reiniciar o Tor para aplicar as novas configurações
echo "Reiniciando o Tor..."
sudo systemctl restart tor

# Aguardar um momento para o Tor reiniciar e gerar o endereço Onion
sleep 10

# Exibir o endereço Onion
if [ -f "$HIDDEN_SERVICE_DIR/hostname" ]; then
    ONION_ADDRESS=$(sudo cat "$HIDDEN_SERVICE_DIR/hostname")
    echo "Seu endereço Onion é: $ONION_ADDRESS"
else
    echo "Falha ao obter o endereço Onion. Verifique se o Tor está configurado corretamente."
fi