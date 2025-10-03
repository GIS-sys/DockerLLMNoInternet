FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*;

RUN pip3 install --break-system-packages --user torch -i https://download.pytorch.org/whl/cpu;
RUN pip3 install --break-system-packages --user transformers;
RUN pip3 install --break-system-packages --user accelerate;

WORKDIR /app/runtime
COPY ./main.py ./main.py
RUN python3 -c "from main import main; main()"

CMD ["python3", "--version"]
#ENTRYPOINT ["python3", "-c"]
#CMD ["from main import main; main('Hello, how are you?')"]

