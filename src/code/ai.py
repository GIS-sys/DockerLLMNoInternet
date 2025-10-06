import huggingface_hub
import torch
print("CUDA", ("is" if torch.cuda.is_available() else "isn't"), "available")
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Dict, Any

from basemodels import PromptRequest, PromptResponse


class Models:
    def __init__(self):
        pass

    @staticmethod
    def get_current_model() -> str:
        return "bbbbb"

    @staticmethod
    def get_models_list() -> list[str]:
        return ["a", "bbbbb", "c"]

    @staticmethod
    def process_request(request: PromptRequest) -> PromptResponse:
        return PromptResponse(**Models.process(request.prompt, request.model_name, request.max_new_tokens))

    @staticmethod
    def process(prompt: str, model_name: str, max_new_tokens: int) -> Dict[str, str]:
        """
        Replace this function with your actual implementation.
        This is a mock function that simulates processing.
        """
        # Simulate some processing logic
        thinking_text = f"Processing prompt: '{prompt}' with model {model_name}"
        final_text = f"Generated response using {model_name} with {max_new_tokens} tokens"
        import time
        time.sleep(1)
        return {
            "thinking": thinking_text,
            "final": final_text
        }

model_name = "Qwen/Qwen3-0.6B"
# model_name = "openai/gpt-oss-20b"

LOCAL_PATH = "../model_cache/" + model_name
SAVE_TO_LOCAL = False








def main(prompt: str = 'Answer with a simple Hello, nothing more'):
    try:
        # local saved
        tokenizer = AutoTokenizer.from_pretrained(LOCAL_PATH, local_files_only=True)
        model = AutoModelForCausalLM.from_pretrained(
            LOCAL_PATH,
            torch_dtype="auto",
            device_map="auto",
            local_files_only=True,
        )
    except (OSError, huggingface_hub.errors.HFValidationError):
        try:
            # local cache
            tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
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
            if SAVE_TO_LOCAL:
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

