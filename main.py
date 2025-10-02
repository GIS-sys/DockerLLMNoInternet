from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Qwen/Qwen3-0.6B"

def main(prompt: str = 'Solve x*2+3=10'):
    # load the tokenizer and the model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto"
    )

    # prepare the model input
    messages = [
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True # Switches between thinking and non-thinking modes. Default is True.
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    # conduct text completion
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=32768
    )
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()

    # parsing thinking content
    try:
        # rindex finding 151668 (</think>)
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0

    thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

    print("thinking content:", thinking_content)
    print("content:", content)

if __name__ == "__main__":
    main()



#import os
#from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
#
#
#cache_dir = "./model_cache"
#model_name = 'LiquidAI/LFM2-350M-Extract'
#PROMPT = """<|startoftext|><|im_start|>system
#Return data as a JSON object with the following schema:
#[...]<|im_end|>
#<|im_start|>user
#Caenorhabditis elegans is a free-living transparent nematode about 1 mm in length that lives in temperate soil environments.<|im_end|>
#<|im_start|>assistant"""
#
#
#def load_model_with_fallback():
#
#    try:
#        # First, try to load from cache without internet
#        print("Attempting to load model from cache...")
#        model = AutoModelForCausalLM.from_pretrained(cache_dir, local_files_only=True)
#        tokenizer = AutoTokenizer.from_pretrained(cache_dir, local_files_only=True)
#        print("✓ Model loaded from local cache")
#        return pipeline('text-generation', model=model, tokenizer=tokenizer)
#
#    except Exception as e:
#        print(f"Model not found in cache: {e}")
#        print("Downloading model (internet connection required)...")
#
#        # Download and cache the model
#        model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=cache_dir)
#        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
#
#        # Explicitly save to our cache directory
#        model.save_pretrained(cache_dir)
#        tokenizer.save_pretrained(cache_dir)
#        print("✓ Model downloaded and cached locally")
#
#        return pipeline('text-generation', model=model, tokenizer=tokenizer)
#
#
#gen = load_model_with_fallback()
#
#result = gen(
#    PROMPT,
#    max_length=50
#)[0]['generated_text']
#
#
#print(result)
