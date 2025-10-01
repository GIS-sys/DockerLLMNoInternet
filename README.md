# Install docker on system without internet (NOT CHECKED)

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
docker build -t my-small-llm .
```

# Run

```bash
docker run my-small-llm
# OR
docker run my-small-llm "from transformers import pipeline; gen = pipeline('text-generation', model='LiquidAI/LFM2-350M-Extract'); print(gen('<|startoftext|><|im_start|>system\\nReturn data as a plain text<|im_end|>\\n<|im_start|>user\\nHello! Explain to me, what is Docker?<|im_end|>\\n<|im_start|>assistant', max_length=50)[0]['generated_text'])"

```

# Package (NOT CHECKED)

```bash
docker save -o my-small-llm.tar my-small-llm
```

# Load on targe machine (NOT CHECKED)

```bash
docker load -i my-small-llm.tar
```

