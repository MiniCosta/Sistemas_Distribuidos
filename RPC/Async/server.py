# server.py
import grpc
from concurrent import futures
import time
import logging
import async_pb2
import async_pb2_grpc

class AsyncService(async_pb2_grpc.AsyncServiceServicer):
    def ProcessTask(self, request, context):
        # Simula um processamento demorado
        print(f"Processando tarefa: {request.task_id}")
        time.sleep(2)  # Simula trabalho pesado
        
        return async_pb2.TaskResponse(
            task_id=request.task_id,
            status="COMPLETED",
            result=f"Resultado para {request.task_id}"
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    async_pb2_grpc.add_AsyncServiceServicer_to_server(AsyncService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Servidor gRPC rodando na porta 50051...")
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()