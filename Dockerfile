# --- TARGET 1: SIMPLE ---
FROM python:3.11 AS simple 
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["streamlit","run","app/main.py","--server.port=8501","--server.address=0.0.0.0"]

# --- TARGET 2: OPTIMIZED ---
FROM python:3.11-slim AS builder 
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS optimized 
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8501
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]

# --- TARGET 3: SECURE (The "Hardened" Phase - Fixed) ---

# Stage 1: Build dependencies on a full OS
FROM python:3.11-slim-bookworm AS secure-builder 

WORKDIR /app

# Install build tools needed for NumPy/Pandas C-extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install packages to a specific directory
RUN pip install --no-cache-dir --target=/app/packages -r requirements.txt

# Stage 2: Final secure image
# Use the 'debug' version of Distroless as it contains vital C-libraries (glibc)
FROM gcr.io/distroless/python3-debian12:debug AS secure 

WORKDIR /app

# Copy the libraries from the builder
COPY --from=secure-builder /app/packages /app/packages

# Copy only your source code
COPY app/ ./app/

# Tell Python where to find the libraries
ENV PYTHONPATH=/app/packages

# Expose Streamlit port
EXPOSE 8501

# In Distroless, we call the module directly via the python interpreter
ENTRYPOINT ["python3", "-m", "streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]