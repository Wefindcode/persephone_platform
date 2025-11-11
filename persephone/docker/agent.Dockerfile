FROM nvidia/cuda:12.2.2-runtime-ubuntu22.04

WORKDIR /workspace

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

COPY persephone/agent /workspace/agent

RUN pip3 install --no-cache-dir pynvml

CMD ["python3", "agent/agent.py", "run"]
