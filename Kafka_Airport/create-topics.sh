#!/bin/bash

# Script para criar os tópicos do aeroporto
echo "Aguardando Kafka inicializar..."
sleep 30

echo "Criando tópico 'chegada'..."
docker exec kafka kafka-topics --create --topic chegada --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

echo "Criando tópico 'partida'..."
docker exec kafka kafka-topics --create --topic partida --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

echo "Listando tópicos criados:"
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

echo "Tópicos do aeroporto criados com sucesso!"
