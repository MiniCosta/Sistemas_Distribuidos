FROM python:3.11-slim

WORKDIR /app

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY src/ ./src/

# Expor porta
EXPOSE 5000

# Variáveis de ambiente padrão
ENV PROCESS_ID=0
ENV PORT=5000

# Comando para iniciar a aplicação
CMD ["python", "src/process.py"]
