# Use an official Ubuntu base image
FROM ubuntu:22.04

# Set environment variables to avoid interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies, Python3, pip, and a minimal model
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install a lightweight LLM runtime and a model.
# For a truly ~4GB model, you would replace 'pippa' with your chosen model.
# This example uses a tiny model for demonstration and fast builds.
RUN pip3 install torch transformers
RUN python3 -c "from transformers import pipeline; pipeline('text-generation', model='LiquidAI/LFM2-350M-Extract')"

# Set the ENTRYPOINT to the Python interpreter
ENTRYPOINT ["python3", "-c"]

# Set a default command that uses the model. This can be overridden at runtime.
CMD ["from transformers import pipeline; gen = pipeline('text-generation', model='LiquidAI/LFM2-350M-Extract'); print(gen('<|startoftext|><|im_start|>system\\nReturn data as a JSON object with the following schema:\\n[...]<|im_end|>\\n<|im_start|>user\\nCaenorhabditis elegans is a free-living transparent nematode about 1 mm in length that lives in temperate soil environments.<|im_end|>\\n<|im_start|>assistant', max_length=50)[0]['generated_text'])"]

