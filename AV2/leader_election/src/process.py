"""
Processo do Sistema Distribuído com Eleição de Líder (Algoritmo Bully)
"""
import os
import logging
import threading
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from bully_algorithm import BullyAlgorithm

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar aplicação Flask
app = Flask(__name__)
CORS(app)

# Configuração do processo
PROCESS_ID = int(os.getenv('PROCESS_ID', '0'))
PORT = int(os.getenv('PORT', '5000'))

# Lista de todos os processos (configurar baseado no ambiente)
# Em Kubernetes, usar service discovery
# Localmente, usar localhost com portas diferentes
if os.getenv('KUBERNETES_SERVICE_HOST'):
    # Ambiente Kubernetes
    ALL_PROCESSES = [
        {'id': 0, 'url': 'http://process-0:5000'},
        {'id': 1, 'url': 'http://process-1:5000'},
        {'id': 2, 'url': 'http://process-2:5000'}
    ]
else:
    # Ambiente local
    ALL_PROCESSES = [
        {'id': 0, 'url': 'http://localhost:5000'},
        {'id': 1, 'url': 'http://localhost:5001'},
        {'id': 2, 'url': 'http://localhost:5002'}
    ]

# Inicializar algoritmo Bully
bully = BullyAlgorithm(PROCESS_ID, ALL_PROCESSES)

# Thread para monitoramento periódico do coordenador
def coordinator_monitor():
    """Thread que monitora a saúde do coordenador periodicamente"""
    while True:
        time.sleep(5)  # Verificar a cada 5 segundos
        
        if not bully.is_coordinator and not bully.in_election:
            is_healthy = bully.check_coordinator_health()
            
            if not is_healthy:
                logger.warning(f"Process {PROCESS_ID} detected coordinator failure!")
                logger.info(f"Process {PROCESS_ID} starting election due to coordinator failure")
                bully.start_election()


# Iniciar thread de monitoramento
monitor_thread = threading.Thread(target=coordinator_monitor, daemon=True)
monitor_thread.start()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint para Kubernetes"""
    return jsonify({
        "status": "healthy",
        "process_id": PROCESS_ID
    }), 200


@app.route('/status', methods=['GET'])
def get_status():
    """Retorna status atual do processo"""
    status = bully.get_status()
    return jsonify(status), 200


@app.route('/election', methods=['POST'])
def election():
    """
    Endpoint para receber mensagem ELECTION
    
    Body: {"from_process": <id>}
    """
    data = request.get_json()
    from_process = data.get('from_process')
    
    if from_process is None:
        # Se não tem from_process, é uma requisição para iniciar eleição
        result = bully.start_election()
        return jsonify(result), 200
    else:
        # Responder à eleição de outro processo
        result = bully.handle_election_request(from_process)
        return jsonify(result), 200


@app.route('/answer', methods=['POST'])
def answer():
    """
    Endpoint para receber mensagem ANSWER
    
    Body: {"from_process": <id>}
    """
    data = request.get_json()
    from_process = data.get('from_process')
    
    logger.info(f"Process {PROCESS_ID} received ANSWER from {from_process}")
    
    return jsonify({
        "status": "acknowledged",
        "process_id": PROCESS_ID
    }), 200


@app.route('/coordinator', methods=['POST'])
def coordinator():
    """
    Endpoint para receber anúncio de novo coordenador
    
    Body: {"coordinator_id": <id>}
    """
    data = request.get_json()
    coordinator_id = data.get('coordinator_id')
    
    if coordinator_id is None:
        return jsonify({
            "error": "coordinator_id is required"
        }), 400
    
    result = bully.handle_coordinator_announcement(coordinator_id)
    return jsonify(result), 200


@app.route('/trigger-election', methods=['POST'])
def trigger_election():
    """Endpoint para forçar início de uma eleição (útil para testes)"""
    result = bully.start_election()
    return jsonify(result), 200


if __name__ == '__main__':
    logger.info(f"Starting Process {PROCESS_ID} on port {PORT}")
    logger.info(f"Initial coordinator: {bully.coordinator_id}")
    logger.info(f"Is coordinator: {bully.is_coordinator}")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)
