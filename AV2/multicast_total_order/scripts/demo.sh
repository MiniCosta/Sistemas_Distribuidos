#!/bin/bash
# Script de demonstração do Multicast com Ordenação Total
# Executar dentro do cluster Kubernetes (usar kubectl exec ou um pod de teste)

echo "=========================================="
echo "  DEMO: Multicast com Ordenação Total    "
echo "=========================================="

# URLs dos serviços (ajustar se necessário)
P0="http://process-0:5000"
P1="http://process-1:5000"
P2="http://process-2:5000"

echo ""
echo "📊 Verificando status dos processos..."
echo "---"
curl -s $P0/status | python3 -m json.tool 2>/dev/null || echo "P0: offline"
curl -s $P1/status | python3 -m json.tool 2>/dev/null || echo "P1: offline"
curl -s $P2/status | python3 -m json.tool 2>/dev/null || echo "P2: offline"

echo ""
echo "=========================================="
echo "  TESTE 1: Envio Sequencial              "
echo "=========================================="

echo ""
echo "📤 P0 envia 'Mensagem A'..."
curl -s -X POST $P0/send -H "Content-Type: application/json" -d '{"content": "Mensagem A"}' | python3 -m json.tool
sleep 2

echo ""
echo "📤 P1 envia 'Mensagem B'..."
curl -s -X POST $P1/send -H "Content-Type: application/json" -d '{"content": "Mensagem B"}' | python3 -m json.tool
sleep 2

echo ""
echo "📤 P2 envia 'Mensagem C'..."
curl -s -X POST $P2/send -H "Content-Type: application/json" -d '{"content": "Mensagem C"}' | python3 -m json.tool
sleep 2

echo ""
echo "=========================================="
echo "  VERIFICANDO ORDEM DE ENTREGA           "
echo "=========================================="

echo ""
echo "📋 Mensagens processadas por P0:"
curl -s $P0/processed | python3 -m json.tool

echo ""
echo "📋 Mensagens processadas por P1:"
curl -s $P1/processed | python3 -m json.tool

echo ""
echo "📋 Mensagens processadas por P2:"
curl -s $P2/processed | python3 -m json.tool

echo ""
echo "=========================================="
echo "  TESTE 2: Envio Simultâneo              "
echo "=========================================="

echo ""
echo "📤 Enviando 3 mensagens simultaneamente..."
curl -s -X POST $P0/send -H "Content-Type: application/json" -d '{"content": "Simultanea 0"}' &
curl -s -X POST $P1/send -H "Content-Type: application/json" -d '{"content": "Simultanea 1"}' &
curl -s -X POST $P2/send -H "Content-Type: application/json" -d '{"content": "Simultanea 2"}' &
wait
sleep 3

echo ""
echo "📋 Verificando ordenação total..."
echo ""
echo "P0 processou:"
curl -s $P0/processed | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f\"  {i+1}. {m['content']} (ts={m['timestamp']}, from=P{m['sender_id']})\") for i,m in enumerate(d['processed'])]"

echo ""
echo "P1 processou:"
curl -s $P1/processed | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f\"  {i+1}. {m['content']} (ts={m['timestamp']}, from=P{m['sender_id']})\") for i,m in enumerate(d['processed'])]"

echo ""
echo "P2 processou:"
curl -s $P2/processed | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f\"  {i+1}. {m['content']} (ts={m['timestamp']}, from=P{m['sender_id']})\") for i,m in enumerate(d['processed'])]"

echo ""
echo "=========================================="
echo "  ✅ Demonstração concluída!             "
echo "=========================================="
echo ""
echo "Se a ordenação total estiver funcionando,"
echo "todos os processos devem ter processado"
echo "as mensagens na MESMA ORDEM."
