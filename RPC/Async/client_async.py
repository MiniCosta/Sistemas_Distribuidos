# client_async.py
# Cliente RPC Assíncrono usando gRPC e asyncio
# Demonstra como enviar múltiplas requisições sem bloquear o programa
# 
# PADRÃO RPC ASSÍNCRONO:
# - Permite enviar múltiplas requisições simultaneamente
# - O programa continua executando enquanto aguarda respostas
# - Ideal para operações I/O-bound (rede, disco, banco de dados)
# - Melhora a eficiência e responsividade da aplicação
#
# DIFERENÇA DO RPC SÍNCRONO:
# - RPC Síncrono: Cliente envia requisição → BLOQUEIA → Recebe resposta → Próxima requisição
# - RPC Assíncrono: Cliente envia N requisições → Continua trabalhando → Recebe N respostas

import grpc
import asyncio
import async_pb2  # Módulo gerado pelo protoc com as mensagens definidas no .proto
import async_pb2_grpc  # Módulo gerado pelo protoc com os stubs do serviço
import time
from concurrent import futures

class AsyncRPCClient:
    """
    Cliente RPC que utiliza chamadas assíncronas para comunicação com o servidor.
    Permite enviar múltiplas requisições simultaneamente sem bloquear a execução.
    """
    def __init__(self):
        # Estabelece conexão insegura (sem SSL/TLS) com o servidor na porta 50051
        self.channel = grpc.insecure_channel('localhost:50051')
        
        # Cria o stub (objeto que representa o serviço remoto) para fazer chamadas RPC
        self.stub = async_pb2_grpc.AsyncServiceStub(self.channel)
    
    async def send_task_async(self, task_id):
        """
        Envia uma tarefa de forma assíncrona para o servidor gRPC.
        
        Como o gRPC padrão é síncrono (bloqueante), esta função usa run_in_executor
        para executar a chamada RPC em uma thread separada, permitindo que o event loop
        do asyncio continue processando outras tarefas enquanto aguarda a resposta.
        
        Args:
            task_id: Identificador único da tarefa a ser processada
            
        Returns:
            TaskResponse: Resposta do servidor com status e resultado
            None: Em caso de erro na comunicação
        """
        # Obtém o event loop atual do asyncio
        loop = asyncio.get_event_loop()
        
        try:
            # Executa a chamada gRPC em uma thread separada (ThreadPoolExecutor padrão)
            # Isso evita bloquear o event loop principal do asyncio
            response = await loop.run_in_executor(
                None,  # None usa o executor padrão (ThreadPoolExecutor)
                lambda: self.stub.ProcessTask(
                    async_pb2.TaskRequest(task_id=task_id)
                )
            )
            return response
        except grpc.RpcError as e:
            # Captura erros específicos do gRPC (timeout, conexão perdida, etc.)
            print(f"Erro na chamada RPC: {e}")
            return None

async def main():
    """
    Função principal que demonstra o padrão de comunicação RPC assíncrona.
    
    Fluxo do programa:
    1. Cria o cliente RPC
    2. Envia múltiplas tarefas simultaneamente (não-bloqueante)
    3. Realiza outras operações locais enquanto aguarda respostas
    4. Coleta todas as respostas quando ficarem prontas
    """
    # Instancia o cliente RPC
    client = AsyncRPCClient()
    
    print("Iniciando envio de tarefas assíncronas...")
    
    # Lista para armazenar as tasks (corrotinas) do asyncio
    tasks = []
    
    # Envia múltiplas tarefas simultaneamente
    for i in range(5):
        # create_task agenda a execução da corrotina sem bloquear
        # A tarefa começa a ser executada em background imediatamente
        task = asyncio.create_task(client.send_task_async(f"task-{i}"))
        tasks.append(task)
        print(f"Tarefa {i} enviada, continuando processamento...")
    
    # IMPORTANTE: O programa continua executando enquanto as requisições RPC
    # estão sendo processadas pelo servidor em paralelo
    print("Processando outras operações...")
    for i in range(3):
        # Simula processamento local (não bloqueia as chamadas RPC)
        await asyncio.sleep(0.5)
        print(f"Operação local {i+1} concluída")
    
    print("Aguardando respostas das tarefas remotas...")
    
    # gather() aguarda todas as tasks terminarem e retorna os resultados
    # return_exceptions=True faz com que exceções sejam retornadas ao invés de propagadas
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Exibe os resultados recebidos do servidor
    print("\n--- Resultados Recebidos ---")
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            # Task retornou uma exceção
            print(f"Tarefa {i}: ERRO - {result}")
        elif result:
            # Task retornou uma resposta válida
            print(f"Tarefa {i}: {result.task_id} - {result.status} - {result.result}")
        else:
            # Task não retornou resposta (erro tratado no send_task_async)
            print(f"Tarefa {i}: Sem resposta")

if __name__ == '__main__':
    # asyncio.run() cria um novo event loop, executa a corrotina main() e fecha o loop
    # É o ponto de entrada padrão para programas asyncio
    asyncio.run(main())