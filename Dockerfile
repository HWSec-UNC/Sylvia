# /hwsec-unc-sylvia/Dockerfile
FROM python:3.10-slim

# System deps for z3 / graphviz / etc
RUN apt-get update && apt-get install -y \
    build-essential zlib1g-dev libffi-dev libgmp-dev graphviz iverilog && \
    apt-get clean

WORKDIR /app

RUN apt-get update && \
    apt-get install -y graphviz graphviz-dev pkg-config && \
    rm -rf /var/lib/apt/lists/*
    
# Install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install any system scripts (sylviaInstall.sh)
COPY sylviaInstall.sh .
RUN chmod +x sylviaInstall.sh && ./sylviaInstall.sh

# Copy the rest of Sylvia
COPY . .
#can write to out.txt
RUN chmod -R 777 /app

EXPOSE 8001

CMD ["uvicorn", "API.sylvia_api:app", "--host", "0.0.0.0", "--port", "8001", "--timeout-keep-alive", "0"]
