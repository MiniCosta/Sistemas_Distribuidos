# Comparação de Complexidade dos Algoritmos de Exclusão Mútua

## 📊 Análise Detalhada

### Métrica: Número de mensagens para entrar na Região Crítica

| Algoritmo           | Complexidade | Requisição | Concessão | Liberação | Total  |
| ------------------- | ------------ | ---------- | --------- | --------- | ------ |
| **Token Ring**      | O(1) a O(n)  | 0          | 0         | 1         | 1 a n  |
| **Centralizado** ✅ | **O(2)**     | **1**      | **1**     | **0**     | **2**  |
| Descentralizado     | O(3√n)       | √n         | √n        | √n        | 3√n    |
| Ricart-Agrawala     | O(2(n-1))    | n-1        | 0         | n-1       | 2(n-1) |

---

## 🥇 Ranking (do menor para o maior)

### 1. Token Ring - O(1) a O(n)

**Melhor caso:** O(1) - processo já tem o token
**Pior caso:** O(n) - token está no processo mais distante
**Média:** O(n/2)

**Vantagens:**

- 🟢 Melhor caso muito eficiente
- 🟢 Simples de implementar
- 🟢 Fairness garantido (anel)

**Desvantagens:**

- 🔴 Perda do token = sistema para
- 🔴 Latência variável
- 🔴 Processo sem interesse atrasa sistema

---

### 2. Centralizado - O(2) ✅ **[ESCOLHIDO]**

**Sempre:** 2 mensagens (REQUEST + GRANT)

**Vantagens:**

- 🟢 **Complexidade constante e previsível**
- 🟢 **Mais eficiente em média**
- 🟢 Fácil de implementar e debugar
- 🟢 Fairness fácil (FIFO)
- 🟢 Fácil adicionar métricas e monitoramento

**Desvantagens:**

- 🔴 Ponto único de falha (coordenador)
- 🔴 Gargalo em alta carga

**Por que é o melhor para este projeto:**

- ✅ Menor complexidade garantida
- ✅ Performance previsível
- ✅ Ideal para demonstração
- ✅ Facilita validação de corretude

---

### 3. Descentralizado - O(3√n)

**Exemplo:** n=16 processos → 3√16 = 12 mensagens

**Vantagens:**

- 🟢 Tolerante a falhas (votação distribuída)
- 🟢 Melhor que totalmente distribuído em escala
- 🟢 Sem ponto único de falha

**Desvantagens:**

- 🔴 Mais complexo de implementar
- 🔴 Overhead de votação
- 🔴 Conflitos possíveis (quorum)

---

### 4. Ricart-Agrawala (Distribuído) - O(2(n-1))

**Exemplo:** n=5 processos → 2(5-1) = 8 mensagens

**Vantagens:**

- 🟢 Totalmente distribuído
- 🟢 Sem coordenador central
- 🟢 Robusto a falhas individuais

**Desvantagens:**

- 🔴 **Maior complexidade** - cresce linearmente com n
- 🔴 Broadcast para todos os processos
- 🔴 Todos precisam responder
- 🔴 Dificuldade em detectar falhas

---

## 📈 Comparação Gráfica

```
Mensagens vs Número de Processos (n)

Token Ring (média):
n=4  → 2 msgs
n=8  → 4 msgs
n=16 → 8 msgs

Centralizado: ✅
n=4  → 2 msgs
n=8  → 2 msgs
n=16 → 2 msgs  (CONSTANTE!)

Descentralizado:
n=4  → 6 msgs
n=9  → 9 msgs
n=16 → 12 msgs

Ricart-Agrawala:
n=4  → 6 msgs
n=8  → 14 msgs
n=16 → 30 msgs
```

---

## 🎯 Conclusão

### Ordem de Complexidade (melhor → pior):

1. **Token Ring**: O(1) no melhor caso, mas O(n) no pior
2. **Centralizado** ✅: **O(2) sempre** - mais consistente
3. **Descentralizado**: O(3√n)
4. **Ricart-Agrawala**: O(2(n-1)) - pior em escala

### Por que Centralizado é o melhor para AV2:

✅ **Complexidade garantida**: Sempre 2 mensagens  
✅ **Performance previsível**: Não depende de n  
✅ **Simplicidade**: Mais fácil demonstrar corretude  
✅ **Prático**: Ideal para demonstração em Kubernetes  
✅ **Métricas claras**: Fácil de monitorar e validar

---

## 📚 Referências

- Tanenbaum & van Steen - "Distributed Systems: Principles and Paradigms"
- Coulouris et al. - "Distributed Systems: Concepts and Design"
- Original papers: Lamport, Ricart-Agrawala, Raymond

---

**Nota para apresentação:**
Use este documento para justificar a escolha do algoritmo **Centralizado** como o mais eficiente em termos de complexidade de mensagens. Ele tem a melhor performance garantida e é ideal para demonstração prática.
