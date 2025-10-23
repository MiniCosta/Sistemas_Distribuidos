#!/bin/bash

echo "🚀 Iniciando Sistema Kafka Airport..."
echo "=================================="

# Verificar se o Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker primeiro."
    exit 1
fi

# Iniciar Kafka
echo "📡 Iniciando Kafka..."
docker-compose up -d

echo "⏳ Aguardando Kafka inicializar (30 segundos)..."
sleep 30

# Criar tópicos
echo "🏗️ Criando tópicos..."
./create-topics.sh

echo ""
echo "✅ Sistema Kafka Airport iniciado com sucesso!"
echo ""
echo "🌐 Interfaces disponíveis:"
echo "   Kafka UI: http://localhost:8080"
echo ""
echo "🎯 Para usar o sistema:"
echo "   1. Instale as dependências: pip install -r requirements.txt"
echo "   2. Execute o produtor: python producer.py"
echo "   3. Execute os consumidores: python consumer_chegada.py (ou consumer_partida.py)"
echo ""
echo "🛑 Para parar o sistema: docker-compose down"
echo "=================================="
