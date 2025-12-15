"""
Multicast com Ordenação Total (Total Order Multicast)
Algoritmo baseado em Lamport com ACKs

Cada processo:
1. Ao enviar mensagem: incrementa relógio, envia msg com (timestamp, process_id) para todos
2. Ao receber mensagem: atualiza relógio, adiciona msg na fila de prioridade, envia ACK
3. Ao receber ACK: registra o ACK para a mensagem
4. Processa mensagem quando: está no topo da fila E recebeu ACK de todos os processos
"""

import os
import random
import threading
import time
import heapq
import requests
from flask import Flask, request, jsonify
from dataclasses import dataclass, field
from typing import Dict, Set
from collections import defaultdict

app = Flask(__name__)

# ============ CONFIGURAÇÕES ============
PROCESS_ID = int(os.environ.get('PROCESS_ID', 0))
NUM_PROCESSES = int(os.environ.get('NUM_PROCESSES', 3))
PORT = int(os.environ.get('PORT', 5000 + PROCESS_ID))  # Porta baseada no ID
DELAY_MODE = os.environ.get('DELAY_MODE', 'false').lower() == 'true'
DELAY_PROCESS = int(os.environ.get('DELAY_PROCESS', 1))  # Processo que vai atrasar
DELAY_MSG_ID = os.environ.get('DELAY_MSG_ID', '')  # ID da msg a atrasar
DELAY_SECONDS = int(os.environ.get('DELAY_SECONDS', 10))

# URLs dos outros processos (serviços Kubernetes)
def get_process_url(pid):
    """Retorna a URL do processo. No K8s, usa o nome do serviço."""
    base_url = os.environ.get(f'PROCESS_{pid}_URL', f'http://process-{pid}:5000')
    return base_url

# ============ ESTADO DO PROCESSO ============
class ProcessState:
    def __init__(self, process_id: int):
        self.process_id = process_id
        self.clock = random.randint(0, 10)  # Relógio lógico inicial aleatório
        self.lock = threading.Lock()
        
        # Fila de prioridade: (timestamp, process_id, msg_id, content)
        # Ordenada por (timestamp, process_id) para desempate
        self.message_queue = []
        
        # Controle de ACKs: msg_id -> set de process_ids que enviaram ACK
        self.acks: Dict[str, Set[int]] = defaultdict(set)
        
        # Mensagens já processadas (para evitar duplicatas)
        self.processed: Set[str] = set()
        
        # Log de mensagens processadas (para demonstração)
        self.processed_log = []
    
    def increment_clock(self):
        """Incrementa o relógio lógico"""
        with self.lock:
            self.clock += 1
            return self.clock
    
    def update_clock(self, received_timestamp: int):
        """Atualiza relógio baseado em timestamp recebido (regra de Lamport)"""
        with self.lock:
            self.clock = max(self.clock, received_timestamp) + 1
            return self.clock
    
    def add_message(self, timestamp: int, sender_id: int, msg_id: str, content: str):
        """Adiciona mensagem na fila de prioridade"""
        with self.lock:
            # Evita duplicatas
            for item in self.message_queue:
                if item[2] == msg_id:
                    return False
            heapq.heappush(self.message_queue, (timestamp, sender_id, msg_id, content))
            return True
    
    def add_ack(self, msg_id: str, from_process: int):
        """Registra ACK recebido"""
        with self.lock:
            self.acks[msg_id].add(from_process)
    
    def can_deliver(self, msg_id: str) -> bool:
        """Verifica se a mensagem pode ser entregue/processada"""
        with self.lock:
            # Precisa ter ACK de todos os processos
            return len(self.acks[msg_id]) >= NUM_PROCESSES
    
    def try_deliver(self):
        """Tenta entregar mensagens que estão prontas"""
        delivered = []
        with self.lock:
            while self.message_queue:
                # Peek no topo da fila
                timestamp, sender_id, msg_id, content = self.message_queue[0]
                
                # Verifica se já foi processada
                if msg_id in self.processed:
                    heapq.heappop(self.message_queue)
                    continue
                
                # Verifica se tem todos os ACKs
                if len(self.acks[msg_id]) >= NUM_PROCESSES:
                    # Remove da fila e processa
                    heapq.heappop(self.message_queue)
                    self.processed.add(msg_id)
                    self.processed_log.append({
                        'msg_id': msg_id,
                        'timestamp': timestamp,
                        'sender_id': sender_id,
                        'content': content,
                        'delivered_at': time.time()
                    })
                    delivered.append((timestamp, sender_id, msg_id, content))
                    print(f"[PROCESS {self.process_id}] ✅ DELIVERED: msg_id={msg_id}, "
                          f"timestamp={timestamp}, from=P{sender_id}, content='{content}'")
                else:
                    # Não pode entregar ainda - aguardando ACKs
                    pending_acks = NUM_PROCESSES - len(self.acks[msg_id])
                    print(f"[PROCESS {self.process_id}] ⏳ WAITING: msg_id={msg_id} needs {pending_acks} more ACKs")
                    break
        
        return delivered
    
    def get_status(self):
        """Retorna status atual do processo"""
        with self.lock:
            queue_info = [(t, p, m, c) for t, p, m, c in self.message_queue]
            return {
                'process_id': self.process_id,
                'clock': self.clock,
                'queue_size': len(self.message_queue),
                'queue': queue_info,
                'acks': {k: list(v) for k, v in self.acks.items()},
                'processed_count': len(self.processed),
                'processed_log': self.processed_log[-10:]  # Últimas 10
            }

# Instância global do estado
state = ProcessState(PROCESS_ID)

# ============ ENDPOINTS DA API ============

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'process_id': PROCESS_ID})

@app.route('/status', methods=['GET'])
def status():
    """Retorna status detalhado do processo"""
    return jsonify(state.get_status())

@app.route('/send', methods=['POST'])
def send_message():
    """
    Endpoint para iniciar envio de mensagem multicast.
    Body: { "content": "mensagem a enviar" }
    
    Este processo vai:
    1. Incrementar seu relógio
    2. Criar msg_id único
    3. Adicionar msg na própria fila
    4. Enviar para todos os outros processos
    5. Enviar ACK para si mesmo E para todos os outros (remetente também envia ACK)
    """
    data = request.json
    content = data.get('content', '')
    
    # Incrementa relógio
    timestamp = state.increment_clock()
    msg_id = f"P{PROCESS_ID}-{timestamp}-{random.randint(1000,9999)}"
    
    print(f"\n[PROCESS {PROCESS_ID}] 📤 SENDING: msg_id={msg_id}, timestamp={timestamp}, content='{content}'")
    
    # Adiciona na própria fila
    state.add_message(timestamp, PROCESS_ID, msg_id, content)
    
    # Envia ACK para si mesmo
    state.add_ack(msg_id, PROCESS_ID)
    
    # Envia para todos os outros processos
    errors = []
    for pid in range(NUM_PROCESSES):
        if pid != PROCESS_ID:
            try:
                url = get_process_url(pid)
                response = requests.post(
                    f"{url}/receive",
                    json={
                        'msg_id': msg_id,
                        'timestamp': timestamp,
                        'sender_id': PROCESS_ID,
                        'content': content
                    },
                    timeout=5
                )
                print(f"[PROCESS {PROCESS_ID}] → Sent to P{pid}: {response.status_code}")
            except Exception as e:
                errors.append(f"P{pid}: {str(e)}")
                print(f"[PROCESS {PROCESS_ID}] ❌ Error sending to P{pid}: {e}")
    
    # IMPORTANTE: O remetente também precisa enviar ACK da própria mensagem para todos
    # Isso garante que todos os processos saibam que o remetente confirmou sua própria msg
    def send_sender_acks():
        for pid in range(NUM_PROCESSES):
            if pid != PROCESS_ID:
                try:
                    url = get_process_url(pid)
                    requests.post(
                        f"{url}/ack",
                        json={
                            'msg_id': msg_id,
                            'from_process': PROCESS_ID
                        },
                        timeout=5
                    )
                    print(f"[PROCESS {PROCESS_ID}] → Sender ACK to P{pid}")
                except Exception as e:
                    print(f"[PROCESS {PROCESS_ID}] ❌ Error sending sender ACK to P{pid}: {e}")
        state.try_deliver()
    
    threading.Thread(target=send_sender_acks, daemon=True).start()
    
    # Tenta entregar mensagens prontas
    state.try_deliver()
    
    return jsonify({
        'success': True,
        'msg_id': msg_id,
        'timestamp': timestamp,
        'errors': errors
    })

@app.route('/receive', methods=['POST'])
def receive_message():
    """
    Endpoint para receber mensagem de outro processo.
    Body: { "msg_id": "...", "timestamp": N, "sender_id": N, "content": "..." }
    
    Este processo vai:
    1. Atualizar seu relógio (regra de Lamport)
    2. Adicionar msg na fila de prioridade
    3. Enviar ACK de volta para TODOS os processos
    """
    data = request.json
    msg_id = data['msg_id']
    timestamp = data['timestamp']
    sender_id = data['sender_id']
    content = data['content']
    
    print(f"\n[PROCESS {PROCESS_ID}] 📥 RECEIVED: msg_id={msg_id}, timestamp={timestamp}, from=P{sender_id}")
    
    # Atualiza relógio
    new_clock = state.update_clock(timestamp)
    
    # Adiciona na fila
    state.add_message(timestamp, sender_id, msg_id, content)
    
    # Envia ACK para TODOS os processos (incluindo remetente original)
    def send_acks():
        # Simula delay se estiver no modo de atraso
        # Se DELAY_MSG_ID está vazio, atrasa TODAS as mensagens
        should_delay = DELAY_MODE and PROCESS_ID == DELAY_PROCESS and (DELAY_MSG_ID == '' or msg_id == DELAY_MSG_ID)
        if should_delay:
            print(f"[PROCESS {PROCESS_ID}] 🐢 DELAYING ACK for {DELAY_SECONDS}s (msg_id={msg_id})...")
            time.sleep(DELAY_SECONDS)
        
        for pid in range(NUM_PROCESSES):
            if pid == PROCESS_ID:
                # ACK para si mesmo
                state.add_ack(msg_id, PROCESS_ID)
            else:
                try:
                    url = get_process_url(pid)
                    response = requests.post(
                        f"{url}/ack",
                        json={
                            'msg_id': msg_id,
                            'from_process': PROCESS_ID
                        },
                        timeout=5
                    )
                    print(f"[PROCESS {PROCESS_ID}] → ACK sent to P{pid}: {response.status_code}")
                except Exception as e:
                    print(f"[PROCESS {PROCESS_ID}] ❌ Error sending ACK to P{pid}: {e}")
        
        # Tenta entregar mensagens prontas
        state.try_deliver()
    
    # Envia ACKs em thread separada para não bloquear a resposta
    threading.Thread(target=send_acks, daemon=True).start()
    
    return jsonify({
        'success': True,
        'new_clock': new_clock
    })

@app.route('/ack', methods=['POST'])
def receive_ack():
    """
    Endpoint para receber ACK de outro processo.
    Body: { "msg_id": "...", "from_process": N }
    """
    data = request.json
    msg_id = data['msg_id']
    from_process = data['from_process']
    
    print(f"[PROCESS {PROCESS_ID}] ✓ ACK received: msg_id={msg_id}, from=P{from_process}")
    
    # Registra o ACK
    state.add_ack(msg_id, from_process)
    
    # Tenta entregar mensagens prontas
    state.try_deliver()
    
    return jsonify({'success': True})

@app.route('/queue', methods=['GET'])
def get_queue():
    """Retorna a fila de mensagens atual"""
    return jsonify({
        'process_id': PROCESS_ID,
        'queue': [(t, p, m, c) for t, p, m, c in state.message_queue]
    })

@app.route('/processed', methods=['GET'])
def get_processed():
    """Retorna log de mensagens processadas"""
    return jsonify({
        'process_id': PROCESS_ID,
        'processed': state.processed_log
    })

# ============ MAIN ============
if __name__ == '__main__':
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║     MULTICAST COM ORDENAÇÃO TOTAL - PROCESSO {PROCESS_ID}              ║
╠══════════════════════════════════════════════════════════════╣
║  Relógio inicial: {state.clock:3d}                                     ║
║  Número de processos: {NUM_PROCESSES}                                    ║
║  Porta: {PORT}                                              ║
║  Modo de delay: {str(DELAY_MODE):5s}                                    ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=PORT, threaded=True)
