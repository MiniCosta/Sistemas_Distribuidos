# Passo a Passo para Rodar e Testar o Kafka Airport (lINUX)

## 1. Instale o Docker
Se ainda não tem Docker instalado:
```bash
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
```

## 2. Instale o Docker Compose (se necessário)
No Ubuntu 22.04+ geralmente já vem, mas se precisar:
```bash
sudo apt install docker-compose
```

## 3. Suba o ambiente Kafka
No diretório `Kafka_Airport`:
```bash
docker-compose up -d
```

## 4. Crie os tópicos necessários
```bash
./create-topics.sh
```

## 5. Instale as dependências Python
```bash
pip install -r requirements.txt
```

## 6. Execute o produtor de voos
Em um terminal:
```bash
python producer.py
```

## 7. Execute os consumidores
Abra novos terminais para cada consumidor:

### Consumidor de chegadas
```bash
python consumer_chegada.py
```

### Consumidor de partidas
```bash
python consumer_partida.py
```

### Consumidor geral (opcional)
```bash
python consumer_geral.py
```

## 8. Teste visualizando as mensagens
- As mensagens de voos de chegada aparecerão no terminal do `consumer_chegada.py`.
- As mensagens de voos de partida aparecerão no terminal do `consumer_partida.py`.
- O consumidor geral mostra ambos.

## 9. Teste via interface web (opcional)
Abra no navegador:
```
http://localhost:8080
```
Veja os tópicos, mensagens, partições e grupos de consumidores.

## 10. Teste manual dos tópicos via linha de comando (opcional)
Para ver mensagens diretamente pelo Kafka:
```bash
# Chegadas
docker exec kafka kafka-console-consumer --topic chegada --bootstrap-server localhost:9092 --from-beginning

# Partidas
docker exec kafka kafka-console-consumer --topic partida --bootstrap-server localhost:9092 --from-beginning
```

## 11. Parar o sistema
```bash
docker-compose down
```

---
Pronto! Agora você pode rodar e testar todas as rotas e tópicos do sistema Kafka Airport.
