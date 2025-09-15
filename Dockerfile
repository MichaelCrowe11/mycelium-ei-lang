# Multi-stage Dockerfile for Mycelium-EI-Lang
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy source code
WORKDIR /build
COPY . .

# Install Python dependencies and build
RUN pip install --no-cache-dir build wheel
RUN python -m build

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy built package from builder
COPY --from=builder /build/dist/*.whl /tmp/

# Install Mycelium-EI-Lang
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

# Create working directory
WORKDIR /workspace

# Set environment variables
ENV MYCELIUM_HOME=/workspace
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd -m -s /bin/bash mycelium && \
    chown -R mycelium:mycelium /workspace

USER mycelium

# Default command
CMD ["python", "-m", "mycelium_ei", "--help"]

# Labels
LABEL maintainer="Michael Benjamin Crowe <michael.benjamin.crowe@gmail.com>"
LABEL version="0.1.0"
LABEL description="Bio-inspired programming language with quantum computing"