# About

Repository for running LLMs via docker, especially on machines without access to the Internet (for example, remote server, only accessible via local network or a direct USB drive)

## Preparations:

Install docker on system without internet: for example, follow [the instructions on official website](https://docs.docker.com/engine/install/binaries/#install-daemon-and-client-binaries-on-linux)

# Pipeline

## Build

Go to the root of this repository and run:

```bash
docker build --progress=plain -t fips-llm .
```

You may have to try "sudo docker" for this to succeed. Be warned that this will use huge amount of traffic

You need to rerun this only if you change one of the:

- Dockerfile
- environment.yaml
- requirements.txt

## Run

On a machine with access to the internet:

```bash
docker run --rm -v ./src/code:/app/run -v ./src/model_cache:/app/model_cache -v ./src/huggingface:/root/.cache/huggingface --gpus all fips-llm python -u -c 'from main import main; main('\''Answer shortly: what is 2+2*2?'\'')'
```

On a machine without the internet:

```bash
docker run --rm -v ./src/code:/app/run -v ./src/model_cache:/app/model_cache -v ./src/huggingface:/root/.cache/huggingface --gpus all fips-llm /bin/bash -c "HF_HUB_OFFLINE=1 python -u -c 'from main import main; main('\''Answer shortly: what is 2+2*2?'\'')'"
```

On Windows you might need to change ./src to .\src and ./src/huggingface to .\src\huggingface

You need to rerun this only if you change main.py AND this change downloads something in one of the volumes (like src/model_cache/ for models or huggingface/ for transformers cache)

## Package

### Docker image

If you have run docker build this iteration - save docker image:

```bash
docker save -o fips-llm.tar fips-llm
```

transfer the fips-llm.tar file and then load it on the target machine:

```bash
docker load -i fips-llm.tar
```

### Volumes

Only transfer this folder if volumes were changed. You don't need to rebuild docker image each time volumes change

### Main script

Only transfer this if the main.py was changed. You don't need to rebuild docker image each time main.py changes

### In general

You could just package and deliver the whole src/ folder, but it will be very large in size, so choose wisely

# Useful info

- Use https://transfer.it/start for transferring huge files and folders between computers. BEWARE that this doesn't preserve symlinks

- To preserve symlinks, use archives to save folder:

  ```bash
  tar --preserve-permissions -czvf SOMEFOLDER.tar.gz SOMEFOLDER/
  ```

  and to extract that later on the remote machine:

  ```bash
  tar -xzvf SOMEFOLDER.tar.gz
  ```
