"""
Coordenador Centralizado para Exclusão Mútua Distribuída
AV2 - Sistemas Distribuídos

Algoritmo: Centralizado
- Mantém fila FIFO de requisições
- Concede acesso exclusivo à região crítica
- Garante exclusão mútua e fairness
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging
from collections import deque
import uvicorn

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mutual Exclusion Coordinator")


class RequestMessage(BaseModel):
    process_id: str
    timestamp: float


class ReleaseMessage(BaseModel):
    process_id: str


class StatusResponse(BaseModel):
    current_holder: Optional[str]
    queue_size: int
    queue: List[str]
    total_requests: int
    total_grants: int
    total_releases: int


class MetricsResponse(BaseModel):
    total_requests: int
    total_grants: int
    total_releases: int
    avg_wait_time: float
    current_queue_size: int


class Coordinator:
    """Coordenador Centralizado para Exclusão Mútua"""
    
    def __init__(self):
        self.current_holder: Optional[str] = None
        self.queue: deque = deque()  # FIFO queue
        self.request_times: dict = {}  # Para calcular tempo de espera
        
        # Métricas
        self.total_requests = 0
        self.total_grants = 0
        self.total_releases = 0
        self.wait_times: List[float] = []
        
        logger.info("🚀 Coordenador inicializado")
    
    def request_access(self, process_id: str, timestamp: float) -> tuple[bool, Optional[str]]:
        """
        Processar requisição de acesso à região crítica
        
        Returns:
            (granted, message): Se acesso foi concedido imediatamente e mensagem
        """
        self.total_requests += 1
        self.request_times[process_id] = datetime.now()
        
        logger.info(f"📨 REQUEST de {process_id} (total: {self.total_requests})")
        
        # Se ninguém está na região crítica, conceder imediatamente
        if self.current_holder is None:
            self.current_holder = process_id
            self.total_grants += 1
            
            # Calcular tempo de espera (zero neste caso)
            wait_time = 0
            self.wait_times.append(wait_time)
            
            logger.info(f"✅ GRANT para {process_id} (imediato)")
            return True, "GRANT"
        
        # Caso contrário, adicionar à fila
        if process_id not in self.queue:
            self.queue.append(process_id)
            logger.info(f"⏳ {process_id} adicionado à fila. Posição: {len(self.queue)}")
        
        return False, "QUEUED"
    
    def release_access(self, process_id: str) -> Optional[str]:
        """
        Liberar região crítica e conceder ao próximo da fila
        
        Returns:
            process_id do próximo processo ou None
        """
        if self.current_holder != process_id:
            logger.warning(f"⚠️  {process_id} tentou liberar mas não é o holder ({self.current_holder})")
            raise HTTPException(
                status_code=400,
                detail=f"Process {process_id} is not the current holder"
            )
        
        self.total_releases += 1
        logger.info(f"🔓 RELEASE de {process_id} (total releases: {self.total_releases})")
        
        # Liberar o holder atual
        self.current_holder = None
        
        # Conceder ao próximo da fila
        if self.queue:
            next_process = self.queue.popleft()
            self.current_holder = next_process
            self.total_grants += 1
            
            # Calcular tempo de espera
            if next_process in self.request_times:
                wait_time = (datetime.now() - self.request_times[next_process]).total_seconds()
                self.wait_times.append(wait_time)
                del self.request_times[next_process]
            
            logger.info(f"✅ GRANT para {next_process} (da fila, grants: {self.total_grants})")
            return next_process
        
        logger.info("💤 Região crítica livre, sem processos na fila")
        return None
    
    def get_status(self) -> StatusResponse:
        """Obter status atual do coordenador"""
        return StatusResponse(
            current_holder=self.current_holder,
            queue_size=len(self.queue),
            queue=list(self.queue),
            total_requests=self.total_requests,
            total_grants=self.total_grants,
            total_releases=self.total_releases
        )
    
    def get_metrics(self) -> MetricsResponse:
        """Obter métricas de performance"""
        avg_wait = sum(self.wait_times) / len(self.wait_times) if self.wait_times else 0
        
        return MetricsResponse(
            total_requests=self.total_requests,
            total_grants=self.total_grants,
            total_releases=self.total_releases,
            avg_wait_time=avg_wait,
            current_queue_size=len(self.queue)
        )


# Instância global do coordenador
coordinator = Coordinator()


@app.post("/request")
async def request_access(msg: RequestMessage):
    """Requisitar acesso à região crítica"""
    granted, status = coordinator.request_access(msg.process_id, msg.timestamp)
    
    return {
        "process_id": msg.process_id,
        "granted": granted,
        "status": status,
        "queue_position": len(coordinator.queue) if not granted else 0
    }


@app.post("/release")
async def release_access(msg: ReleaseMessage):
    """Liberar região crítica"""
    next_process = coordinator.release_access(msg.process_id)
    
    return {
        "process_id": msg.process_id,
        "released": True,
        "next_granted": next_process
    }


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Obter status atual do coordenador"""
    return coordinator.get_status()


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Obter métricas de performance"""
    return coordinator.get_metrics()


@app.get("/health")
async def health_check():
    """Health check para Kubernetes"""
    return {"status": "healthy", "service": "coordinator"}


@app.get("/")
async def root():
    """Endpoint raiz"""
    status = coordinator.get_status()
    return {
        "service": "Mutual Exclusion Coordinator",
        "algorithm": "Centralized",
        "status": status.dict()
    }


if __name__ == "__main__":
    logger.info("🎯 Iniciando Coordenador Centralizado...")
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
