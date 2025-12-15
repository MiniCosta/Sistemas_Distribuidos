"""
Implementação do Algoritmo Bully (Valentão) para Eleição de Líder
"""
import time
import logging
from typing import Optional, List
import requests

logger = logging.getLogger(__name__)


class BullyAlgorithm:
    def __init__(self, process_id: int, all_processes: List[dict]):
        """
        Inicializa o algoritmo Bully
        
        Args:
            process_id: ID único do processo (maior ID = maior prioridade)
            all_processes: Lista de todos os processos [{id, url}, ...]
        """
        self.process_id = process_id
        self.all_processes = sorted(all_processes, key=lambda x: x['id'])
        self.coordinator_id: Optional[int] = None
        self.is_coordinator = False
        self.in_election = False
        
        # Encontrar o coordenador inicial (maior ID)
        max_process = max(self.all_processes, key=lambda x: x['id'])
        self.coordinator_id = max_process['id']
        self.is_coordinator = (self.process_id == self.coordinator_id)
        
        logger.info(f"Process {self.process_id} initialized. Initial coordinator: {self.coordinator_id}")
    
    def get_higher_processes(self) -> List[dict]:
        """Retorna lista de processos com ID maior que o atual"""
        return [p for p in self.all_processes if p['id'] > self.process_id]
    
    def get_lower_processes(self) -> List[dict]:
        """Retorna lista de processos com ID menor que o atual"""
        return [p for p in self.all_processes if p['id'] < self.process_id]
    
    def send_election_message(self, target_url: str) -> bool:
        """
        Envia mensagem ELECTION para um processo
        
        Returns:
            True se recebeu resposta ANSWER, False caso contrário
        """
        try:
            response = requests.post(
                f"{target_url}/election",
                json={"from_process": self.process_id},
                timeout=2
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Failed to send election to {target_url}: {e}")
            return False
    
    def send_answer_message(self, target_url: str) -> bool:
        """Envia mensagem ANSWER para um processo"""
        try:
            response = requests.post(
                f"{target_url}/answer",
                json={"from_process": self.process_id},
                timeout=2
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Failed to send answer to {target_url}: {e}")
            return False
    
    def send_coordinator_message(self, target_url: str) -> bool:
        """Anuncia que este processo é o novo coordenador"""
        try:
            response = requests.post(
                f"{target_url}/coordinator",
                json={"coordinator_id": self.process_id},
                timeout=2
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Failed to send coordinator to {target_url}: {e}")
            return False
    
    def start_election(self) -> dict:
        """
        Inicia uma eleição seguindo o algoritmo Bully
        
        Returns:
            Dicionário com resultado da eleição
        """
        if self.in_election:
            logger.info(f"Process {self.process_id} already in election")
            return {
                "status": "already_in_election",
                "process_id": self.process_id
            }
        
        self.in_election = True
        logger.info(f"Process {self.process_id} starting election")
        
        # Passo 1: Enviar ELECTION para todos os processos com ID maior
        higher_processes = self.get_higher_processes()
        
        if not higher_processes:
            # Se não há processos com ID maior, este é o coordenador
            logger.info(f"Process {self.process_id} has highest ID, becoming coordinator")
            self.become_coordinator()
            self.in_election = False
            return {
                "status": "elected",
                "coordinator_id": self.process_id,
                "message": "No higher processes, became coordinator"
            }
        
        # Enviar mensagens de eleição
        responses = []
        for process in higher_processes:
            if process['id'] != self.process_id:
                success = self.send_election_message(process['url'])
                responses.append(success)
                if success:
                    logger.info(f"Process {self.process_id} received ANSWER from {process['id']}")
        
        # Passo 2: Verificar se alguém respondeu
        if any(responses):
            # Alguém respondeu, aguardar novo coordenador ser anunciado
            logger.info(f"Process {self.process_id} received answers, waiting for coordinator announcement")
            self.in_election = False
            return {
                "status": "waiting",
                "process_id": self.process_id,
                "message": "Higher processes responded, waiting for coordinator"
            }
        else:
            # Ninguém respondeu, tornar-se coordenador
            logger.info(f"Process {self.process_id} received no answers, becoming coordinator")
            self.become_coordinator()
            self.in_election = False
            return {
                "status": "elected",
                "coordinator_id": self.process_id,
                "message": "No responses, became coordinator"
            }
    
    def become_coordinator(self):
        """Torna este processo o coordenador e anuncia para todos"""
        self.is_coordinator = True
        self.coordinator_id = self.process_id
        
        logger.info(f"Process {self.process_id} is now the COORDINATOR")
        
        # Anunciar para todos os processos com ID menor
        lower_processes = self.get_lower_processes()
        for process in lower_processes:
            if process['id'] != self.process_id:
                success = self.send_coordinator_message(process['url'])
                if success:
                    logger.info(f"Announced coordinator to process {process['id']}")
    
    def handle_election_request(self, from_process: int) -> dict:
        """
        Trata requisição ELECTION de outro processo
        
        Args:
            from_process: ID do processo que iniciou a eleição
        
        Returns:
            Resposta para enviar
        """
        logger.info(f"Process {self.process_id} received ELECTION from {from_process}")
        
        if from_process < self.process_id:
            # Responder com ANSWER e iniciar própria eleição
            logger.info(f"Process {self.process_id} sending ANSWER to {from_process}")
            
            # Enviar ANSWER de volta (implícito na resposta HTTP 200)
            # Iniciar própria eleição
            self.start_election()
            
            return {
                "status": "answer",
                "process_id": self.process_id,
                "message": "Starting own election"
            }
        else:
            return {
                "status": "ignored",
                "process_id": self.process_id,
                "message": "Election from higher or equal process ignored"
            }
    
    def handle_coordinator_announcement(self, coordinator_id: int) -> dict:
        """
        Trata anúncio de novo coordenador
        
        Args:
            coordinator_id: ID do novo coordenador
        """
        logger.info(f"Process {self.process_id} received COORDINATOR announcement: {coordinator_id}")
        
        self.coordinator_id = coordinator_id
        self.is_coordinator = (coordinator_id == self.process_id)
        self.in_election = False
        
        return {
            "status": "acknowledged",
            "process_id": self.process_id,
            "coordinator_id": self.coordinator_id
        }
    
    def check_coordinator_health(self) -> bool:
        """
        Verifica se o coordenador atual está ativo
        
        Returns:
            True se coordenador está ativo, False caso contrário
        """
        if self.is_coordinator:
            return True
        
        coordinator = next((p for p in self.all_processes if p['id'] == self.coordinator_id), None)
        if not coordinator:
            return False
        
        try:
            response = requests.get(f"{coordinator['url']}/health", timeout=2)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Coordinator {self.coordinator_id} health check failed: {e}")
            return False
    
    def get_status(self) -> dict:
        """Retorna status atual do processo"""
        return {
            "process_id": self.process_id,
            "is_coordinator": self.is_coordinator,
            "coordinator_id": self.coordinator_id,
            "in_election": self.in_election,
            "all_processes": [p['id'] for p in self.all_processes]
        }
