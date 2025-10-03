FROM ubuntu:24.04


WORKDIR /app

ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
ENV DEBIAN_FRONTEND=noninteractive


RUN apt-get update --fix-missing && DEBIAN_FRONTEND=noninteractive apt-get install --assume-yes --no-install-recommends \
    wget bash libxau-dev git;
# install miniconda
RUN arch=$(uname -m) && \
    if [ "$arch" = "x86_64" ]; then \
    MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"; \
    elif [ "$arch" = "aarch64" ]; then \
    MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh"; \
    else \
    echo "Unsupported architecture: $arch"; \
    exit 1; \
    fi && \
    wget --no-check-certificate $MINICONDA_URL -O miniconda.sh && \
    mkdir -p /root/.conda;
RUN bash miniconda.sh -b -p /root/miniconda3;
RUN rm -f miniconda.sh;

RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r;


COPY environment.yaml ./environment.yaml
RUN export PIP_LOG="/tmp/pip_log.txt" && \
    touch ${PIP_LOG} && \
    tail -f ${PIP_LOG} & conda env create --name llm --file=environment.yaml -v;

SHELL ["conda", "run", "-n", "llm", "--no-capture-output", "/bin/bash", "-c"]


WORKDIR /app/run
# COPY ./main.py ./main.py
# RUN python -c "from main import main; main()"


ENTRYPOINT ["conda", "run", "-n", "llm", "--no-capture-output", "/bin/bash", "-c"]
CMD ["python -c 'import torch; print(torch.cuda.is_available()); from main import main; main()'"]

