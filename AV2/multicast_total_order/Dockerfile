# Imagem base Python slim
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Copia arquivos de dependências
COPY requirements.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY app.py .

# Expõe porta 5000
EXPOSE 5000

# Variáveis de ambiente padrão
ENV PROCESS_ID=0
ENV NUM_PROCESSES=3
ENV DELAY_MODE=false

# Comando para iniciar
CMD ["python", "app.py"]
