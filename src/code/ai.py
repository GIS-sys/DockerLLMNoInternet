import gc
import huggingface_hub
import torch
print("CUDA", ("is" if torch.cuda.is_available() else "isn't"), "available")
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Dict, Any

from basemodels import PromptRequest, PromptResponse


SAVE_TO_LOCAL = False
MODELS = ["Qwen/Qwen3-0.6B", "openai/gpt-oss-20b"]


class Models:
    initialized = False
    current_model = ""

    @classmethod
    def init(cls):
        if cls.initialized:
            return
        cls.initialized = True
        cls.load_model(cls.get_models_list()[0])

    @classmethod
    def get_current_model(cls) -> str:
        cls.init()
        return cls.current_model

    @classmethod
    def get_current_local_path(cls) -> str:
        cls.init()
        return "../model_cache/" + cls.get_current_model()

    @classmethod
    def get_models_list(cls) -> list[str]:
        cls.init()
        return MODELS

    @classmethod
    def process_request(cls, request: PromptRequest) -> PromptResponse:
        cls.init()
        return PromptResponse(**Models.process(prompt=request.prompt, model_name=request.model_name, max_new_tokens=request.max_new_tokens))

    @classmethod
    def unload_model(cls):
        cls.model = cls.model.to('cpu')
        del cls.model
        del cls.tokenizer
        torch.cuda.empty_cache()
        gc.collect()
        cls.current_model = ""

    @classmethod
    def load_model(cls, model_name: str):
        cls.init()
        if cls.get_current_model() == model_name:
            return
        if cls.get_current_model() != "":
            cls.unload_model()
            # raise Exception(f"Can't load a new model {model_name} when the last model {cls.get_current_model()} was loaded. Aborting")
        cls.current_model = model_name
        try:
            # local saved
            cls.tokenizer = AutoTokenizer.from_pretrained(cls.get_current_local_path(), local_files_only=True)
            cls.model = AutoModelForCausalLM.from_pretrained(
                cls.get_current_local_path(),
                torch_dtype="auto",
                device_map="auto",
                local_files_only=True,
            )
        except (OSError, huggingface_hub.errors.HFValidationError):
            try:
                # local cache
                cls.tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
                cls.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype="auto",
                    device_map="auto",
                    local_files_only=True,
                )
            except (OSError, huggingface_hub.errors.HFValidationError):
                # load the tokenizer and the model
                cls.tokenizer = AutoTokenizer.from_pretrained(model_name)
                cls.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype="auto",
                    device_map="auto",
                )
                if SAVE_TO_LOCAL:
                    cls.tokenizer.save_pretrained(cls.get_current_local_path())
                    cls.model.save_pretrained(cls.get_current_local_path())

    @classmethod
    def parse_response(cls, model_name: str, response: str) -> tuple[str, str]:
        if "<think>" in response and "</think>" in response:
            tmp = response
            tmp = tmp[tmp.index("<think>") + len("<think>"):]
            thinking = tmp[:tmp.index("</think>")].strip("\n")
            final = tmp[tmp.index("</think>") + len("</think>"):].strip("\n")
            return thinking, final
        if "analysis" in response and "assistantfinal" in response:
            tmp = response
            tmp = tmp[tmp.index("analysis") + len("analysis"):]
            thinking = tmp[:tmp.index("assistantfinal")].strip("\n")
            final = tmp[tmp.index("assistantfinal") + len("assistantfinal"):].strip("\n")
            return thinking, final
        return "", response

    @classmethod
    def process(cls, model_name: str, max_new_tokens: int = 32768, prompt: str = "Answer with a simple Hello, nothing more") -> Dict[str, str]:
        cls.init()
        cls.load_model(model_name)

        # prepare the model input
        messages = [
            {"role": "user", "content": prompt}
        ]
        text = cls.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=True,
        )
        model_inputs = cls.tokenizer([text], return_tensors="pt").to(cls.model.device)
        # conduct text completion
        generated_ids = cls.model.generate(
            **model_inputs,
            max_new_tokens=max_new_tokens,
        )
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
        response = cls.tokenizer.decode(output_ids, skip_special_tokens=True)
        thinking, final = cls.parse_response(model_name=model_name, response=response)
        return {
            "thinking": thinking,
            "final": final,
        }

