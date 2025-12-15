# Guia de Demonstração - AV2

## Exclusão Mútua Distribuída

### 🎯 Objetivo da Demonstração

Demonstrar o funcionamento do **algoritmo de exclusão mútua centralizado** em ambiente Kubernetes, mostrando:

1. Garantia de exclusão mútua (apenas 1 processo por vez na RC)
2. Fairness (FIFO - todos os processos acessam eventualmente)
3. Ausência de deadlock
4. Métricas de performance

---

## 📋 Checklist Pré-Demonstração

- [ ] Docker Desktop instalado e rodando
- [ ] Minikube instalado
- [ ] kubectl instalado e configurado
- [ ] Python 3.9+ (opcional, apenas se testar localmente)

---

## 🚀 Passo a Passo da Demonstração

### 1. Preparar o Ambiente

```powershell
# Navegar para o diretório do projeto
cd "C:\Users\paulo\Desktop\Code\Sistemas_Distribuidos\AV2\mutual_exclusion"

# Verificar se Minikube está instalado
minikube version

# Verificar se Docker está rodando
docker ps
```

### 2. Iniciar Minikube

```powershell
# Iniciar cluster Kubernetes local
minikube start --driver=docker

# Verificar status
minikube status
```

**Explicar:** Minikube cria um cluster Kubernetes local usando Docker

---

### 3. Deploy da Aplicação

```powershell
# Executar script de deploy
.\scripts\deploy.ps1
```

**O que acontece:**

1. ✅ Configura Docker para usar daemon do Minikube
2. ✅ Constrói imagem do Coordinator
3. ✅ Constrói imagem dos Processes
4. ✅ Cria namespace `mutual-exclusion`
5. ✅ Deploy do coordinator (1 réplica)
6. ✅ Deploy dos processes (4 réplicas)

**Explicar:**

- **Coordinator**: Servidor centralizado que gerencia acesso à RC
- **Processes**: Clientes que competem pelo acesso à RC

---

### 4. Verificar Pods

```powershell
# Listar pods
kubectl get pods -n mutual-exclusion -o wide

# Ver detalhes
kubectl describe pods -n mutual-exclusion
```

**Mostrar:**

- 1 pod do coordinator
- 4 pods de processes
- Status: Running

---

### 5. Monitorar Logs do Coordinator

**Abrir novo terminal** e executar:

```powershell
cd "C:\Users\paulo\Desktop\Code\Sistemas_Distribuidos\AV2\mutual_exclusion"
.\scripts\logs.ps1 -Component coordinator
```

**Explicar o que aparece nos logs:**

- 📨 `REQUEST` - Processo requisita acesso
- ✅ `GRANT` - Coordenador concede acesso
- ⏳ Processos sendo adicionados à fila FIFO
- 🔓 `RELEASE` - Processo libera RC
- 🎉 Próximo processo recebe permissão

---

### 6. Executar Testes e Monitoramento

**No terminal principal:**

```powershell
.\scripts\test.ps1
```

**O que o script faz:**

1. Configura port-forward para o coordinator (porta 5000)
2. Monitora status em tempo real (a cada 3s)
3. Mostra a cada iteração:
   - 🔒 Quem está na região crítica
   - 📋 Fila de espera (FIFO)
   - 📈 Estatísticas (requests, grants, releases)
   - ⚡ Métricas de performance (tempo médio de espera)

---

### 7. Demonstrar Exclusão Mútua

**Pontos a destacar durante o monitoramento:**

#### ✅ Exclusão Mútua Garantida

- Apenas **1 processo por vez** na região crítica
- Nunca aparece 2 processos simultaneamente

#### ✅ Fairness (FIFO)

- Processos são atendidos na ordem de chegada
- Todos os 4 processos eventualmente acessam a RC
- Ver ordem na fila sendo respeitada

#### ✅ Progresso

- Sistema nunca trava
- Sempre há um próximo processo quando RC é liberada
- Throughput constante

#### ✅ Ausência de Deadlock

- Não há ciclos de espera
- Coordenador controla tudo centralmente

---

### 8. Analisar Métricas

O script de teste mostra:

```
📈 Estatísticas:
   Requisições: 45
   Concessões:  45
   Liberações:  44

⚡ Métricas de Performance:
   Tempo médio de espera: 8.5s
   Tamanho atual da fila: 2
```

**Explicar:**

- **Requisições**: Total de pedidos recebidos
- **Concessões**: Total de acessos concedidos
- **Liberações**: Total de RCs liberadas
- **Tempo de espera**: Quanto tempo processo aguarda para entrar na RC

---

### 9. Verificar Algoritmo no Código

**Mostrar pontos-chave do código:**

#### Coordinator (`coordinator/app.py`):

```python
# Fila FIFO para garantir fairness
self.queue: deque = deque()

# Apenas 1 holder por vez (exclusão mútua)
self.current_holder: Optional[str] = None
```

#### Process (`process/app.py`):

```python
# Ciclo de exclusão mútua:
# 1. REQUEST
granted = await request_critical_section()

# 2. WAIT (polling)
if not granted:
    granted = await wait_for_grant()

# 3. CRITICAL SECTION
await execute_critical_section()

# 4. RELEASE
await release_critical_section()
```

---

### 10. Demonstrar Escalabilidade

```powershell
# Aumentar número de processos
kubectl scale deployment process --replicas=8 -n mutual-exclusion

# Verificar novos pods
kubectl get pods -n mutual-exclusion

# Ver logs atualizados
# (O monitoramento do test.ps1 mostrará mais processos competindo)
```

**Explicar:** O algoritmo continua funcionando com mais processos, mas:

- Tempo de espera aumenta (mais concorrência)
- Fila fica maior
- Throughput por processo diminui

---

## 📊 Comparação de Algoritmos

**Explicar por que escolhemos o Centralizado:**

| Algoritmo        | Mensagens/RC | Complexidade | Vantagens                 | Desvantagens              |
| ---------------- | ------------ | ------------ | ------------------------- | ------------------------- |
| Token Ring       | O(1) ~ O(n)  | Baixa        | Simples, baixa latência   | Perda de token = problema |
| **Centralizado** | **O(2)**     | **Baixa**    | **Simples, justo (FIFO)** | **Ponto único de falha**  |
| Descentralizado  | O(3√n)       | Média        | Tolerante a falhas        | Mais complexo             |
| Ricart-Agrawala  | O(2(n-1))    | Alta         | Totalmente distribuído    | Muitas mensagens          |

**Centralizado é ideal para:**

- ✅ Ambientes controlados (como este demo)
- ✅ Performance previsível
- ✅ Implementação simples e fácil de entender
- ✅ Debugging facilitado

---

## 🧹 Limpeza

```powershell
# Parar monitoramento (Ctrl+C nos terminais)

# Limpar recursos do Kubernetes
.\scripts\cleanup.ps1

# (Opcional) Parar Minikube
minikube stop
```

---

## 🎤 Roteiro de Fala

### Introdução (1 min)

"Implementei o algoritmo de **Exclusão Mútua Centralizado** porque tem a **menor complexidade de mensagens** (O(2)) e é o mais **eficiente** para demonstração. Vou mostrar rodando no **Kubernetes com Minikube**."

### Demonstração (3-4 min)

1. "Aqui temos o coordinator (1 pod) e 4 processos competindo pela região crítica"
2. "Nos logs, vemos REQUEST-GRANT-RELEASE garantindo exclusão mútua"
3. "A fila FIFO garante que todos os processos acessam (fairness)"
4. "Métricas mostram throughput constante e tempo de espera controlado"
5. "Escalando para 8 processos, o algoritmo continua funcionando perfeitamente"

### Conclusão (1 min)

"O algoritmo centralizado garante **exclusão mútua**, **fairness** e **ausência de deadlock** com apenas **2 mensagens por acesso**, sendo o mais eficiente em complexidade de comunicação."

---

## ⚠️ Troubleshooting

### Erro: Pods não iniciam

```powershell
kubectl describe pod -n mutual-exclusion <pod-name>
```

**Solução:** Verificar se imagens foram construídas corretamente

### Erro: Port-forward falha

```powershell
# Parar processos pendentes
Get-Process kubectl -ErrorAction SilentlyContinue | Stop-Process -Force
```

### Erro: Minikube não inicia

```powershell
minikube delete
minikube start --driver=docker
```

---

## 📚 Recursos Adicionais

- **README.md**: Documentação completa do projeto
- **coordinator/app.py**: Implementação do coordenador
- **process/app.py**: Implementação dos processos
- **k8s/\*.yaml**: Configurações Kubernetes

---

**Boa sorte na apresentação! 🚀**
