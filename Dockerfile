# Use the specified Ubuntu base image
FROM ubuntu:24.04

# Set environment variables to avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    bash \
    libxau-dev \
    git \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download and install Miniforge3 (which includes mamba)
RUN wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname -s)-$(uname -m).sh -O miniforge_install.sh && \
    bash miniforge_install.sh -b -p /opt/miniforge3 && \
    rm miniforge_install.sh

# Add Miniforge3 to the system PATH
ENV PATH="/opt/miniforge3/bin:${PATH}"

# Make RUN commands use the bash shell
SHELL ["/bin/bash", "-c"]

# Copy the environment file and create the Conda environment
COPY environment.yaml /tmp/environment.yaml
RUN yes Y | mamba env create -v -f /tmp/environment.yaml

# Activate the environment and set PATH for subsequent commands
# The environment name is extracted from the environment.yaml file
RUN echo "source activate $(head -1 /tmp/environment.yaml | cut -d' ' -f2)" > ~/.bashrc
ENV PATH /opt/miniforge3/envs/$(head -1 /tmp/environment.yaml | cut -d' ' -f2)/bin:$PATH

RUN which python

COPY requirements.txt /tmp/requirements.txt
RUN yes | pip install -r /tmp/requirements.txt

WORKDIR /app/run

# Default command: test PyTorch and CUDA
CMD ["python", "-u", "-c", "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"]
