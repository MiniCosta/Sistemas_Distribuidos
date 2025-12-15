"""
Processo Cliente para Exclusão Mútua Distribuída
AV2 - Sistemas Distribuídos

Este processo:
1. Requisita acesso ao coordenador
2. Aguarda permissão (polling)
3. Executa na região crítica
4. Libera o acesso
5. Repete após intervalo aleatório
"""

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import httpx
import asyncio
import logging
import os
import time
import random
from datetime import datetime
from typing import List, Optional
import uvicorn

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mutual Exclusion Process")

# Configurações
PROCESS_ID = os.getenv("PROCESS_ID", f"process-{random.randint(1000, 9999)}")
COORDINATOR_URL = os.getenv("COORDINATOR_URL", "http://localhost:5000")
CRITICAL_SECTION_DURATION = float(os.getenv("CS_DURATION", "3"))  # segundos
REQUEST_INTERVAL_MIN = float(os.getenv("INTERVAL_MIN", "5"))
REQUEST_INTERVAL_MAX = float(os.getenv("INTERVAL_MAX", "15"))


class AccessRecord(BaseModel):
    timestamp: float
    duration: float
    success: bool
    wait_time: float


class ProcessState:
    """Estado do processo"""
    
    def __init__(self):
        self.process_id = PROCESS_ID
        self.in_critical_section = False
        self.access_history: List[AccessRecord] = []
        self.total_requests = 0
        self.total_accesses = 0
        self.is_running = False
        
        logger.info(f"🎲 Processo {self.process_id} inicializado")
    
    def add_record(self, record: AccessRecord):
        """Adicionar registro de acesso"""
        self.access_history.append(record)
        if record.success:
            self.total_accesses += 1


state = ProcessState()


async def request_critical_section() -> bool:
    """
    Requisitar acesso à região crítica ao coordenador
    
    Returns:
        True se acesso foi concedido imediatamente, False se foi enfileirado
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{COORDINATOR_URL}/request",
                json={
                    "process_id": state.process_id,
                    "timestamp": time.time()
                }
            )
            response.raise_for_status()
            data = response.json()
            
            granted = data.get("granted", False)
            status = data.get("status", "UNKNOWN")
            
            if granted:
                logger.info(f"✅ Acesso CONCEDIDO imediatamente")
            else:
                queue_pos = data.get("queue_position", "?")
                logger.info(f"⏳ Acesso em fila. Status: {status}, Posição: {queue_pos}")
            
            return granted
            
    except Exception as e:
        logger.error(f"❌ Erro ao requisitar acesso: {e}")
        return False


async def wait_for_grant(max_wait: float = 120.0) -> bool:
    """
    Aguardar até receber permissão do coordenador (polling)
    
    Args:
        max_wait: Tempo máximo de espera em segundos
    
    Returns:
        True se recebeu permissão, False se timeout
    """
    start_time = time.time()
    poll_interval = 0.5  # segundos
    
    while time.time() - start_time < max_wait:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{COORDINATOR_URL}/status")
                response.raise_for_status()
                status = response.json()
                
                if status.get("current_holder") == state.process_id:
                    logger.info(f"🎉 Permissão CONCEDIDA! Entrando na região crítica")
                    return True
                
        except Exception as e:
            logger.warning(f"⚠️  Erro ao verificar status: {e}")
        
        await asyncio.sleep(poll_interval)
    
    logger.error(f"⏰ Timeout aguardando permissão ({max_wait}s)")
    return False


async def release_critical_section():
    """Liberar região crítica"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{COORDINATOR_URL}/release",
                json={"process_id": state.process_id}
            )
            response.raise_for_status()
            data = response.json()
            
            next_process = data.get("next_granted")
            if next_process:
                logger.info(f"🔓 Região crítica liberada. Próximo: {next_process}")
            else:
                logger.info(f"🔓 Região crítica liberada. Fila vazia.")
                
    except Exception as e:
        logger.error(f"❌ Erro ao liberar região crítica: {e}")


async def execute_critical_section():
    """Simular execução na região crítica"""
    logger.info(f"🔒 ENTRANDO na região crítica...")
    state.in_critical_section = True
    
    # Simular trabalho na região crítica
    await asyncio.sleep(CRITICAL_SECTION_DURATION)
    
    # Simular escrita em recurso compartilhado
    logger.info(f"📝 Executando operação crítica (incremento de contador)")
    
    state.in_critical_section = False
    logger.info(f"🚪 SAINDO da região crítica")


async def mutual_exclusion_cycle():
    """
    Ciclo completo de exclusão mútua:
    1. REQUEST
    2. WAIT (se necessário)
    3. CRITICAL SECTION
    4. RELEASE
    """
    state.total_requests += 1
    request_start = time.time()
    
    logger.info(f"🎯 Iniciando ciclo #{state.total_requests}")
    
    try:
        # 1. Requisitar acesso
        granted = await request_critical_section()
        
        # 2. Se não foi concedido, aguardar
        if not granted:
            granted = await wait_for_grant()
        
        if not granted:
            # Timeout - registrar falha
            record = AccessRecord(
                timestamp=request_start,
                duration=0,
                success=False,
                wait_time=time.time() - request_start
            )
            state.add_record(record)
            return
        
        wait_time = time.time() - request_start
        logger.info(f"⏱️  Tempo de espera: {wait_time:.2f}s")
        
        # 3. Executar região crítica
        cs_start = time.time()
        await execute_critical_section()
        cs_duration = time.time() - cs_start
        
        # 4. Liberar acesso
        await release_critical_section()
        
        # Registrar sucesso
        record = AccessRecord(
            timestamp=request_start,
            duration=cs_duration,
            success=True,
            wait_time=wait_time
        )
        state.add_record(record)
        
        logger.info(f"✨ Ciclo #{state.total_requests} concluído com sucesso")
        
    except Exception as e:
        logger.error(f"💥 Erro no ciclo de exclusão mútua: {e}")
        
        record = AccessRecord(
            timestamp=request_start,
            duration=0,
            success=False,
            wait_time=time.time() - request_start
        )
        state.add_record(record)


async def run_continuous():
    """Executar ciclos de exclusão mútua continuamente"""
    state.is_running = True
    logger.info(f"🏃 Iniciando execução contínua do processo {state.process_id}")
    
    # Aguardar inicialização
    await asyncio.sleep(random.uniform(1, 5))
    
    while state.is_running:
        await mutual_exclusion_cycle()
        
        # Intervalo aleatório entre requisições
        interval = random.uniform(REQUEST_INTERVAL_MIN, REQUEST_INTERVAL_MAX)
        logger.info(f"😴 Aguardando {interval:.1f}s até próxima requisição...")
        await asyncio.sleep(interval)


@app.on_event("startup")
async def startup_event():
    """Iniciar execução automática ao subir o serviço"""
    asyncio.create_task(run_continuous())


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "service": "Mutual Exclusion Process",
        "process_id": state.process_id,
        "in_critical_section": state.in_critical_section,
        "total_requests": state.total_requests,
        "total_accesses": state.total_accesses
    }


@app.get("/status")
async def get_status():
    """Obter status do processo"""
    return {
        "process_id": state.process_id,
        "in_critical_section": state.in_critical_section,
        "total_requests": state.total_requests,
        "total_accesses": state.total_accesses,
        "success_rate": state.total_accesses / state.total_requests if state.total_requests > 0 else 0,
        "is_running": state.is_running
    }


@app.get("/history")
async def get_history():
    """Obter histórico de acessos"""
    return {
        "process_id": state.process_id,
        "total_records": len(state.access_history),
        "history": state.access_history[-20:]  # Últimos 20
    }


@app.post("/trigger")
async def trigger_cycle(background_tasks: BackgroundTasks):
    """Forçar uma requisição manual"""
    background_tasks.add_task(mutual_exclusion_cycle)
    return {"message": "Cycle triggered", "process_id": state.process_id}


@app.post("/stop")
async def stop_process():
    """Parar execução contínua"""
    state.is_running = False
    return {"message": "Process stopped", "process_id": state.process_id}


@app.post("/start")
async def start_process():
    """Iniciar execução contínua"""
    if not state.is_running:
        asyncio.create_task(run_continuous())
    return {"message": "Process started", "process_id": state.process_id}


@app.get("/health")
async def health_check():
    """Health check para Kubernetes"""
    return {"status": "healthy", "process_id": state.process_id}


if __name__ == "__main__":
    logger.info(f"🚀 Iniciando processo {PROCESS_ID}...")
    logger.info(f"🎯 Coordenador: {COORDINATOR_URL}")
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
