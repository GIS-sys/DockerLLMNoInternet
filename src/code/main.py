import huggingface_hub
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
print("CUDA", ("is" if torch.cuda.is_available() else "isn't"), "available")


model_name = "Qwen/Qwen3-0.6B"
# model_name = "openai/gpt-oss-20b"

LOCAL_PATH = "../model_cache/" + model_name


def main(prompt: str = 'Answer with a simple Hello, nothing more'):
    try:
        # local
        tokenizer = AutoTokenizer.from_pretrained(LOCAL_PATH)
        model = AutoModelForCausalLM.from_pretrained(
            LOCAL_PATH,
            torch_dtype="auto",
            device_map="auto",
            local_files_only=True,
        )
    except (OSError, huggingface_hub.errors.HFValidationError):
        # load the tokenizer and the model
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto",
        )
        tokenizer.save_pretrained(LOCAL_PATH)
        model.save_pretrained(LOCAL_PATH)

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
