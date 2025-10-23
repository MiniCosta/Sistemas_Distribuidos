# Sistema Kafka Airport ✈️

Sistema publish-subscribe usando Apache Kafka para simular o sistema de informações de um aeroporto, monitorando voos de chegada e partida.

## 📋 Requisitos Implementados

### 1. ✅ Instância Kafka via Container
- Docker Compose com Zookeeper, Kafka e Kafka UI
- Configuração completa para desenvolvimento local

### 2. ✅ Tópicos Criados
- **2.1 Chegada**: Tópico para voos que chegam ao aeroporto
- **2.2 Partida**: Tópico para voos que partem do aeroporto

### 3. ✅ Aplicação Produtora
- **3.1 Voos de chegada**: Gera dados simulados de voos chegando
- **3.2 Voos de partida**: Gera dados simulados de voos partindo
- Dados realistas com companhias aéreas, aeroportos brasileiros, horários e status

### 4. ✅ Aplicação Consumidora
- **4.1 Voos de chegada**: Consumidor específico para chegadas
- **4.2 Voos de partida**: Consumidor específico para partidas
- **4.3 Monitor geral**: Consumidor que monitora ambos os tópicos

## 🚀 Como Executar

### Pré-requisitos
- Docker e Docker Compose instalados
- Python 3.7+ instalado
- pip (gerenciador de pacotes Python)

### Passo 1: Iniciar o Kafka
```bash
cd Kafka_Airport
docker-compose up -d
```

### Passo 2: Criar os Tópicos
```bash
./create-topics.sh
```

### Passo 3: Instalar Dependências Python
```bash
pip install -r requirements.txt
```

### Passo 4: Executar as Aplicações

#### Iniciar o Produtor (em um terminal):
```bash
python producer.py
```

#### Iniciar Consumidores (em terminais separados):

**Consumidor de Chegadas:**
```bash
python consumer_chegada.py
```

**Consumidor de Partidas:**
```bash
python consumer_partida.py
```

**Monitor Geral (todos os voos):**
```bash
python consumer_geral.py
```

## 🎛️ Kafka UI

Acesse a interface web do Kafka em: http://localhost:8080

Permite visualizar:
- Tópicos criados
- Mensagens em tempo real
- Partições e offsets
- Grupos de consumidores

## 📊 Estrutura dos Dados

### Exemplo de Mensagem de Voo:
```json
{
    "flight_number": "GO1234",
    "airline": "GOL",
    "aircraft_type": "Boeing 737",
    "origin": "GRU",
    "destination": "CGH",
    "scheduled_time": "2024-10-23 14:30:00",
    "status": "No horário",
    "gate": "G5",
    "terminal": "2",
    "passengers": 180,
    "flight_type": "chegada",
    "timestamp": "2024-10-23T12:00:00",
    "actual_time": "2024-10-23 14:45:00",  // Opcional, quando há atraso
    "delay_minutes": 15                     // Opcional, quando há atraso
}
```

## 📁 Estrutura do Projeto

```
Kafka_Airport/
├── docker-compose.yml          # Configuração do Kafka
├── create-topics.sh           # Script para criar tópicos
├── requirements.txt           # Dependências Python
├── producer.py               # Produtor de voos
├── consumer_chegada.py       # Consumidor de chegadas
├── consumer_partida.py       # Consumidor de partidas
├── consumer_geral.py         # Monitor geral
└── README.md                 # Esta documentação
```

## 🎯 Funcionalidades

### Produtor
- Gera voos de chegada e partida aleatoriamente
- Dados realistas: companhias brasileiras, aeroportos, horários
- Status variados: no horário, atrasado, cancelado, embarcando, etc.
- Particionamento por número do voo
- Frequência configurável (padrão: 3 segundos)

### Consumidores
- **Chegada**: Monitora apenas voos chegando ao aeroporto
- **Partida**: Monitora apenas voos saindo do aeroporto  
- **Geral**: Monitor central que acompanha todos os voos
- Interface colorida com emojis para melhor visualização
- Informações detalhadas de cada voo

## 🛠️ Comandos Úteis

### Verificar status dos containers:
```bash
docker-compose ps
```

### Ver logs do Kafka:
```bash
docker-compose logs kafka
```

### Parar o sistema:
```bash
docker-compose down
```

### Listar tópicos:
```bash
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

### Ver mensagens de um tópico:
```bash
# Chegadas
docker exec kafka kafka-console-consumer --topic chegada --bootstrap-server localhost:9092 --from-beginning

# Partidas  
docker exec kafka kafka-console-consumer --topic partida --bootstrap-server localhost:9092 --from-beginning
```

## 🚨 Solução de Problemas

### Kafka não inicia:
- Verifique se as portas 2181 e 9092 estão livres
- Aguarde alguns segundos para o Zookeeper inicializar primeiro

### Erro de conexão Python:
- Confirme que o Kafka está rodando: `docker-compose ps`
- Verifique se as dependências estão instaladas: `pip list`

### Tópicos não criados:
- Execute novamente: `./create-topics.sh`
- Verifique os logs: `docker-compose logs kafka`

## 🎨 Exemplo de Saída

```
🛬 CHEGADA - GO1234 ✅
   Companhia: GOL
   Aeronave: Boeing 737
   Origem: GRU → Destino: CGH
   Horário Programado: 2024-10-23 14:30:00
   Status: No horário
   Portão: G5 | Terminal: 2
   Passageiros: 180
   Recebido em: 14:25:30
```

## 📈 Extensões Possíveis

- Adicionar persistência em banco de dados
- Implementar notificações push
- Interface web em tempo real
- Integração com APIs de companhias aéreas reais
- Sistema de alertas automáticos
- Métricas e dashboards de monitoramento

---
**Sistema Kafka Airport** - Sistema de monitoramento de voos em tempo real usando Apache Kafka
