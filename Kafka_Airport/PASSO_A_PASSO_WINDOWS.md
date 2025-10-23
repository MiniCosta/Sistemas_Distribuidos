# Passo a Passo para Rodar e Testar o Kafka Airport (Windows)

> **Exclusivo para sistemas Windows**

## 1. Instale o Docker Desktop
Baixe e instale o Docker Desktop para Windows:
- https://www.docker.com/products/docker-desktop/

Após instalar, abra o Docker Desktop e certifique-se de que ele está rodando.

## 2. Instale o Python
Baixe e instale o Python 3.7+ em https://www.python.org/downloads/

Durante a instalação, marque a opção "Add Python to PATH".

## 3. Abra o Prompt de Comando ou PowerShell
Navegue até a pasta do projeto `Kafka_Airport`:
```powershell
cd caminho\para\Kafka_Airport
```

## 4. Suba o ambiente Kafka
```powershell
docker-compose up -d
```

## 5. Crie os tópicos necessários
```powershell
./create-topics.sh
```
Se der erro, use:
```powershell
bash create-topics.sh
```
(É necessário ter o Git Bash ou WSL instalado para rodar scripts .sh no Windows)

## 6. Instale as dependências Python
```powershell
pip install -r requirements.txt
```

## 7. Execute o produtor de voos
Em um terminal:
```powershell
python producer.py
```

## 8. Execute os consumidores
Abra novos terminais para cada consumidor:

### Consumidor de chegadas
```powershell
python consumer_chegada.py
```

### Consumidor de partidas
```powershell
python consumer_partida.py
```

### Consumidor geral (opcional)
```powershell
python consumer_geral.py
```

## 9. Teste visualizando as mensagens
- As mensagens de voos de chegada aparecerão no terminal do `consumer_chegada.py`.
- As mensagens de voos de partida aparecerão no terminal do `consumer_partida.py`.
- O consumidor geral mostra ambos.

## 10. Teste via interface web (opcional)
Abra no navegador:
```
http://localhost:8080
```
Veja os tópicos, mensagens, partições e grupos de consumidores.

## 11. Teste manual dos tópicos via linha de comando (opcional)
Para ver mensagens diretamente pelo Kafka:
```powershell
# Chegadas
docker exec kafka kafka-console-consumer --topic chegada --bootstrap-server localhost:9092 --from-beginning

# Partidas
docker exec kafka kafka-console-consumer --topic partida --bootstrap-server localhost:9092 --from-beginning
```

## 12. Parar o sistema
```powershell
docker-compose down
```

---
Pronto! Agora você pode rodar e testar todas as rotas e tópicos do sistema Kafka Airport no Windows.
