# Multicast com Ordenação Total - AV2 Sistemas Distribuídos

## 📋 Descrição

Implementação do algoritmo de **Multicast com Ordenação Total** baseado em timestamps de Lamport com ACKs. O sistema garante que todas as mensagens são entregues na mesma ordem em todos os processos.

## 🏗️ Arquitetura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Process 0  │◄───►│  Process 1  │◄───►│  Process 2  │
│   (P0)      │     │   (P1)      │     │   (P2)      │
└─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │
      └───────────────────┼───────────────────┘
                          │
                    API REST (Flask)
```

## 🔧 Algoritmo

1. **Envio de Mensagem:**

   - Incrementa relógio lógico
   - Cria ID único: `P{id}-{timestamp}-{random}`
   - Adiciona msg na própria fila de prioridade
   - Envia msg para todos os outros processos
   - Envia ACK para si mesmo

2. **Recebimento de Mensagem:**

   - Atualiza relógio: `clock = max(clock, received_ts) + 1`
   - Adiciona msg na fila de prioridade
   - Envia ACK para TODOS os processos

3. **Entrega de Mensagem:**
   - Mensagem no TOPO da fila
   - Recebeu ACK de TODOS os processos
   - → Processa a mensagem (print na tela)

## 📁 Estrutura do Projeto

```
multicast_total_order/
├── app.py                    # Aplicação principal Flask
├── requirements.txt          # Dependências Python
├── Dockerfile                # Imagem Docker
├── k8s/
│   ├── deployment.yaml       # Deploy normal (3 processos)
│   └── deployment-delay.yaml # Deploy com modo de delay
├── scripts/
│   ├── demo.sh               # Script de demonstração (Linux/K8s)
│   ├── run-local.ps1         # Execução local (Windows)
│   └── test-local.ps1        # Testes locais (Windows)
└── README.md
```

## 🚀 Execução no Kubernetes (Minikube)

### 1. Iniciar Minikube

```bash
minikube start
```

### 2. Configurar Docker do Minikube

```bash
# Linux/Mac
eval $(minikube docker-env)

# Windows PowerShell
& minikube -p minikube docker-env --shell powershell | Invoke-Expression
```

### 3. Build da Imagem

```bash
docker build -t multicast-total-order:latest .
```

### 4. Deploy no Kubernetes

**Modo Normal (sem delay):**

```bash
kubectl apply -f k8s/deployment.yaml
```

**Modo com Delay (para demonstrar bloqueio):**

```bash
kubectl apply -f k8s/deployment-delay.yaml
```

### 5. Verificar Pods

```bash
kubectl get pods -l app=multicast
kubectl logs -f deployment/process-0
```

### 6. Testar (usando port-forward)

```bash
# Em um terminal
kubectl port-forward svc/process-0 5000:5000

# Em outro terminal
curl -X POST http://localhost:5000/send -H "Content-Type: application/json" -d '{"content": "Hello World"}'
```

## 🧪 Execução Local (Windows)

### 1. Instalar dependências

```powershell
pip install -r requirements.txt
```

### 2. Usar script automatizado

```powershell
# Inicia os 3 processos em janelas separadas
.\scripts\run-local.ps1

# Após iniciar, execute os testes (em outro terminal)
.\scripts\test-local.ps1
```

### 3. OU executar manualmente em 3 terminais

```powershell
# Terminal 1 - Processo 0
$env:PROCESS_ID="0"; $env:PORT="5000"; $env:NUM_PROCESSES="3"; $env:PROCESS_0_URL="http://localhost:5000"; $env:PROCESS_1_URL="http://localhost:5001"; $env:PROCESS_2_URL="http://localhost:5002"
python app.py

# Terminal 2 - Processo 1
$env:PROCESS_ID="1"; $env:PORT="5001"; $env:NUM_PROCESSES="3"; $env:PROCESS_0_URL="http://localhost:5000"; $env:PROCESS_1_URL="http://localhost:5001"; $env:PROCESS_2_URL="http://localhost:5002"
python app.py

# Terminal 3 - Processo 2
$env:PROCESS_ID="2"; $env:PORT="5002"; $env:NUM_PROCESSES="3"; $env:PROCESS_0_URL="http://localhost:5000"; $env:PROCESS_1_URL="http://localhost:5001"; $env:PROCESS_2_URL="http://localhost:5002"
python app.py
```

### 4. Testar manualmente

```powershell
# Enviar mensagem via P0
Invoke-RestMethod -Uri "http://localhost:5000/send" -Method Post -ContentType "application/json" -Body '{"content": "Mensagem A"}'

# Enviar via P1
Invoke-RestMethod -Uri "http://localhost:5001/send" -Method Post -ContentType "application/json" -Body '{"content": "Mensagem B"}'

# Enviar via P2
Invoke-RestMethod -Uri "http://localhost:5002/send" -Method Post -ContentType "application/json" -Body '{"content": "Mensagem C"}'

# Ver mensagens processadas por todos
Invoke-RestMethod -Uri "http://localhost:5000/processed"
Invoke-RestMethod -Uri "http://localhost:5001/processed"
Invoke-RestMethod -Uri "http://localhost:5002/processed"
```

## 📡 API Endpoints

| Método | Endpoint     | Descrição                    |
| ------ | ------------ | ---------------------------- |
| GET    | `/health`    | Health check                 |
| GET    | `/status`    | Status completo do processo  |
| POST   | `/send`      | Envia mensagem multicast     |
| POST   | `/receive`   | Recebe mensagem (interno)    |
| POST   | `/ack`       | Recebe ACK (interno)         |
| GET    | `/queue`     | Fila de mensagens atual      |
| GET    | `/processed` | Log de mensagens processadas |

## 🎯 Demonstração

### Cenário 1: Sem Delay (Normal)

1. P0 envia "Mensagem A"
2. P1 envia "Mensagem B"
3. P2 envia "Mensagem C"
4. **Resultado:** Todos os processos entregam na mesma ordem (ordenado por timestamp)

### Cenário 2: Com Delay

1. Reiniciar com modo delay: `.\scripts\run-local.ps1 -DelayMode`
2. P1 **atrasa** o ACK por 10 segundos quando `DELAY_MSG_ID` é definido
3. **Resultado:** P0 e P2 ficam esperando o ACK de P1 antes de processar
4. Demonstra que **TODOS os ACKs são necessários** para ordenação total

## 🔍 Variáveis de Ambiente

| Variável        | Descrição                      | Default / Exemplo                  |
| --------------- | ------------------------------ | ---------------------------------- |
| `PROCESS_ID`    | ID único do processo (0, 1, 2) | 0                                  |
| `NUM_PROCESSES` | Número total de processos      | 3                                  |
| `PORT`          | Porta do servidor Flask        | **Local:** 5000+ID / **K8s:** 5000 |
| `DELAY_MODE`    | Ativa modo de atraso           | false                              |
| `DELAY_PROCESS` | Qual processo vai atrasar      | 1                                  |
| `DELAY_MSG_ID`  | ID da msg a atrasar            | ""                                 |
| `DELAY_SECONDS` | Segundos de atraso             | 10                                 |
| `PROCESS_N_URL` | URL do processo N              | http://process-N:5000              |

**Nota sobre PORT:**

- **Local**: Calculada como `5000 + PROCESS_ID` (P0→5000, P1→5001, P2→5002)
- **Kubernetes**: Fixa em `5000` para todos os pods (definido no deployment.yaml)

## ✅ Critérios Atendidos

- [x] 3 processos instanciados
- [x] API REST para comunicação
- [x] Endpoint para envio de msg (`/send`)
- [x] Endpoint para ACK (`/ack`)
- [x] Mensagens com ID do processo e timestamp
- [x] Constante NUM_PROCESSES para contar ACKs
- [x] Processamento = print na tela
- [x] Fila de prioridade para ordenação
- [x] Tabela hash (dict) para controlar ACKs
- [x] Relógio inteiro com valor inicial aleatório (0-10)
- [x] Incremento a cada envio/recebimento
- [x] Modo sem delay
- [x] Modo com delay em processo específico
- [x] Deploy no Kubernetes (Minikube)
