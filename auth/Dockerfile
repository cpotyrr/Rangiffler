FROM python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    python3-dev \
    build-essential \
    python3-pip \
    rustc \
    cargo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Install wheel first
RUN pip install --no-cache-dir wheel

# Install cryptography separately first
RUN pip install --no-cache-dir cryptography==41.0.7

# Then install the rest of requirements
RUN pip install --no-cache-dir -r requirements.txt

COPY auth/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000", "--reload"]
