"""Model/tokenizer loading with optional 4-bit QLoRA."""

from __future__ import annotations

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def pick_dtype():
    if torch.cuda.is_available():
        return torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    return torch.float32


def load_model_and_tokenizer(model_name: str, adapter: str | None = None,
                             load_4bit: bool = False, for_training: bool = False):
    tok = AutoTokenizer.from_pretrained(model_name)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    kwargs: dict = {"torch_dtype": pick_dtype()}
    cuda = torch.cuda.is_available()

    if load_4bit and cuda:
        from transformers import BitsAndBytesConfig
        kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=pick_dtype(),
            bnb_4bit_use_double_quant=True,
        )
        kwargs["device_map"] = {"": 0}
    elif cuda:
        kwargs["device_map"] = {"": 0}
    else:
        if load_4bit:
            print("[modeling] CUDA not available -> ignoring --load-4bit, using full precision.")

    model = AutoModelForCausalLM.from_pretrained(model_name, **kwargs)

    if adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter)

    if not for_training:
        model.eval()
    return model, tok
