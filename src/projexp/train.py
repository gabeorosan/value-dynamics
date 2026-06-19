"""QLoRA SFT for one arm. No trl dependency — plain transformers Trainer with a
completion-only loss mask (prompt tokens are set to -100).
"""

from __future__ import annotations

import argparse
import json

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import Trainer, TrainingArguments

from .modeling import load_model_and_tokenizer, pick_dtype


def load_examples(path: str) -> list[dict]:
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def make_encoder(tok, max_len: int):
    def encode(ex):
        msgs = ex["messages"]
        # Render to text first, then tokenize -> always plain int lists.
        # (apply_chat_template(tokenize=True) can return tokenizers.Encoding objects
        # on some transformers versions, which breaks the tensor collation.)
        full_text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)
        prompt_text = tok.apply_chat_template(msgs[:-1], tokenize=False, add_generation_prompt=True)
        full = tok(full_text, add_special_tokens=False)["input_ids"]
        prompt = tok(prompt_text, add_special_tokens=False)["input_ids"]
        n_prompt = len(prompt)
        labels = [-100] * n_prompt + full[n_prompt:]
        full, labels = full[:max_len], labels[:max_len]
        return {"input_ids": full, "labels": labels, "attention_mask": [1] * len(full)}
    return encode


class Collator:
    def __init__(self, pad_id: int):
        self.pad_id = pad_id

    def __call__(self, batch):
        maxlen = max(len(b["input_ids"]) for b in batch)
        ids, lab, att = [], [], []
        for b in batch:
            pad = maxlen - len(b["input_ids"])
            ids.append(b["input_ids"] + [self.pad_id] * pad)
            lab.append(b["labels"] + [-100] * pad)
            att.append(b["attention_mask"] + [0] * pad)
        return {
            "input_ids": torch.tensor(ids),
            "labels": torch.tensor(lab),
            "attention_mask": torch.tensor(att),
        }


def main(argv=None):
    ap = argparse.ArgumentParser(description="QLoRA SFT for one arm.")
    ap.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct")
    ap.add_argument("--data", required=True, help="arm_*.jsonl from projexp-gen")
    ap.add_argument("--out", required=True, help="output adapter dir")
    ap.add_argument("--load-4bit", action="store_true")
    ap.add_argument("--max-steps", type=int, default=200)
    ap.add_argument("--epochs", type=float, default=-1, help="if >0, overrides --max-steps")
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--batch-size", type=int, default=2)
    ap.add_argument("--grad-accum", type=int, default=8)
    ap.add_argument("--lora-r", type=int, default=16)
    ap.add_argument("--lora-alpha", type=int, default=32)
    ap.add_argument("--max-len", type=int, default=512)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)

    model, tok = load_model_and_tokenizer(
        args.model, load_4bit=args.load_4bit, for_training=True)
    if args.load_4bit and torch.cuda.is_available():
        model = prepare_model_for_kbit_training(model)
    model.config.use_cache = False

    lora = LoraConfig(
        r=args.lora_r, lora_alpha=args.lora_alpha, lora_dropout=0.05,
        bias="none", task_type="CAUSAL_LM", target_modules="all-linear",
    )
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()

    rows = load_examples(args.data)
    ds = Dataset.from_list(rows).map(
        make_encoder(tok, args.max_len), remove_columns=["messages"])

    cuda = torch.cuda.is_available()
    targs = TrainingArguments(
        output_dir=args.out,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        max_steps=args.max_steps if args.epochs <= 0 else -1,
        num_train_epochs=args.epochs if args.epochs > 0 else 3,
        warmup_ratio=0.03,
        lr_scheduler_type="cosine",
        logging_steps=10,
        save_strategy="no",
        gradient_checkpointing=True,
        bf16=cuda and torch.cuda.is_bf16_supported(),
        fp16=cuda and not torch.cuda.is_bf16_supported(),
        optim="paged_adamw_8bit" if (args.load_4bit and cuda) else "adamw_torch",
        report_to="none",
        seed=args.seed,
    )

    trainer = Trainer(model=model, args=targs, train_dataset=ds,
                      data_collator=Collator(tok.pad_token_id))
    trainer.train()
    model.save_pretrained(args.out)
    tok.save_pretrained(args.out)
    print(f"[train] saved adapter -> {args.out}")


if __name__ == "__main__":
    main()
