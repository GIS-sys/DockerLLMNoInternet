# Install docker on system without internet (NOT TESTED)

1) Download ??? .tgz from https://docs.docker.com/engine/install/binaries/#install-daemon-and-client-binaries-on-linux

2) Copy it on remote server

3) Unpack and run:

``` bash
tar xzvf /path/to/FILE.tar.gz
sudo cp docker/* /usr/bin/
sudo dockerd &
```

# Build

```bash
docker build -t fips-llm .
```

If this takes too long - try sudo

# Run

```bash
docker run -v ./src:/app/run --gpus all fips-llm
# OR
docker run -v ./src:/app/run --gpus all fips-llm "python -c \"from transformers import pipeline; gen = pipeline('text-generation', model='LiquidAI/LFM2-350M-Extract'); print(gen('<|startoftext|><|im_start|>system\\nReturn data as a plain text<|im_end|>\\n<|im_start|>user\\nHello! Explain to me, what is Docker?<|im_end|>\\n<|im_start|>assistant', max_length=50)[0]['generated_text'])\""

```

# Package

```bash
docker save -o fips-llm.tar fips-llm
```

# Load on targe machine

```bash
docker load -i fips-llm.tar
```

