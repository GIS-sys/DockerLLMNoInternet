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
docker build --progress=plain -t fips-llm .
```

If this takes too long - try sudo

# Run

```bash
docker run --rm -v ./src:/app/run --gpus all fips-llm
# OR
docker run --rm -v ./src:/app/run --gpus all fips-llm python -c 'import torch; print(torch.cuda.is_available()); from main import main; main()'

```

On Windows you might need to change ./src to .\src

# Package

```bash
docker save -o fips-llm.tar fips-llm
```

# Load on targe machine

```bash
docker load -i fips-llm.tar
```

