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

# Package

```bash
???
```

# Load on targe machine

```bash
???
```

