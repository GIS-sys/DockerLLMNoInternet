FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*;

RUN pip3 --version && python3 --version && sleep 3;
RUN pip3 install --break-system-packages --user torch -i https://download.pytorch.org/whl/cpu;
RUN pip3 install --break-system-packages --user transformers;
RUN python3 -c "from transformers import pipeline; gen = pipeline('text-generation', model='LiquidAI/LFM2-350M-Extract', model_kwargs={'cache_dir': './model_cache'}); gen('test', max_length=50)";
#RUN python3 -c "from transformers import pipeline;";

ENTRYPOINT ["python3", "-c"]

CMD ["from transformers import pipeline; print(123); gen = pipeline('text-generation', model='LiquidAI/LFM2-350M-Extract'); print(gen('<|startoftext|><|im_start|>system\\nReturn data as a JSON object with the following schema:\\n[...]<|im_end|>\\n<|im_start|>user\\nCaenorhabditis elegans is a free-living transparent nematode about 1 mm in length that lives in temperate soil environments.<|im_end|>\\n<|im_start|>assistant', max_length=50)[0]['generated_text'])"]
#CMD ["from transformers import pipeline; print('Start')"]

