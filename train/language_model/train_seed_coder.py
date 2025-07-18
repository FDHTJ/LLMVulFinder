import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, Sequence
import argparse
import torch
import transformers
import utils
from torch.utils.data import Dataset
from transformers import Trainer, TrainerState, TrainerControl
import numpy as np
from utils import utils
import os
import torch.distributed as dist

IGNORE_INDEX = -100
DEFAULT_PAD_TOKEN = "[PAD]"
DEFAULT_EOS_TOKEN = "</s>"
DEFAULT_BOS_TOKEN = "<s>"
DEFAULT_UNK_TOKEN = "<unk>"
logging.basicConfig(level=logging.DEBUG)
@dataclass
class ModelArguments:
    model_name_or_path: Optional[str] = field(default="Seed-Coder-8B-Instruct")


@dataclass
class DataArguments:
    data_path: str = field(default=f"processed_bigvul_before_after_non_for_seed_coder.jsonl", metadata={"help": "Path to the training data."})
    max_target_length:int=field(default=10240)


@dataclass
class TrainingArguments(transformers.TrainingArguments):
    output_dir: str = field(default=f"output/seed-coder-8B", metadata={"help": "Path to the output directory."})
    cache_dir: Optional[str] = field(default="cache")
    optim: str = field(default="adamw_torch")
    model_max_length: int = field(
        default=4096,
        metadata={"help": "Maximum sequence length. Sequences will be right padded (and possibly truncated)."},
    )
    evaluation_strategy :str =field(default="no")
    eval_steps : int =field(default=30)
    per_device_eval_batch_size: int = field(default=1)
    eval_accumulation_steps : int = field(default=32)
    save_only_model:bool=field(default=True) #only save model when save check point
    truncate_source: bool = field(default=False)
    per_device_train_batch_size: int = field(default=1)
    gradient_accumulation_steps: int = field(default=32)
    num_train_epochs: int = field(default=3)
    learning_rate: float = field(default=5e-5)
    warmup_steps: int = field(default=100)
    weight_decay: float = field(default=0.0)
    logging_steps: int = field(default=1)
    save_steps: int = field(default=20)
    lr_scheduler_type: str = field(default="cosine")
    save_strategy: str = field(default="steps")
    save_total_limit: int = field(default=100)
    report_to: str = field(default="tensorboard")
    fp16: bool = field(default=False)
    tf32: bool = field(default=True)
    gradient_checkpointing: bool = field(default=True)
def smart_tokenizer_and_embedding_resize(
    special_tokens_dict: Dict,
    tokenizer: transformers.PreTrainedTokenizer,
    model: transformers.PreTrainedModel,
):
    """Resize tokenizer and embedding.

    Note: This is the unoptimized version that may make your embedding size not be divisible by 64.
    """
    num_new_tokens = tokenizer.add_special_tokens(special_tokens_dict)
    model.resize_token_embeddings(len(tokenizer))

    if num_new_tokens > 0:
        input_embeddings = model.get_input_embeddings().weight.data
        output_embeddings = model.get_output_embeddings().weight.data

        input_embeddings_avg = input_embeddings[:-num_new_tokens].mean(dim=0, keepdim=True)
        output_embeddings_avg = output_embeddings[:-num_new_tokens].mean(dim=0, keepdim=True)

        input_embeddings[-num_new_tokens:] = input_embeddings_avg
        output_embeddings[-num_new_tokens:] = output_embeddings_avg


def _tokenize_fn(strings: Sequence[str], tokenizer: transformers.PreTrainedTokenizer) -> Dict:
    """Tokenize a list of strings."""
    tokenized_list = [
        tokenizer(
            text,
            return_tensors="pt",
            padding="longest",
            max_length=tokenizer.model_max_length,
            truncation=True,
        )
        for text in strings
    ]
    input_ids = labels = [tokenized.input_ids[0] for tokenized in tokenized_list]
    input_ids_lens = labels_lens = [
        tokenized.input_ids.ne(tokenizer.pad_token_id).sum().item() for tokenized in tokenized_list
    ]
    return dict(
        input_ids=input_ids,
        labels=labels,
        input_ids_lens=input_ids_lens,
        labels_lens=labels_lens,
    )


class SupervisedDataset(Dataset):
    """Dataset for supervised fine-tuning."""

    def __init__(self, data_path: str, tokenizer: transformers.PreTrainedTokenizer, args):
        super(SupervisedDataset, self).__init__()
        logging.warning(f"Loading data from {data_path}...")
        if data_path.endswith(".npy"):
            list_data_dict = np.load(data_path, allow_pickle=True)
        else:
            list_data_dict = utils.read_jsonl_file(data_path)
        logging.info("Loading tokenized sentences...")
        pad_token=-100#tokenizer.pad_token_id
        def truncate(sentence):
            return torch.tensor(sentence[:args.model_max_length] + [tokenizer.eos_token_id] if len(sentence) > args.model_max_length else sentence)
        if args.truncate_source:
            self.input_ids = [truncate(example["input_ids"]) for example in list_data_dict]
            self.labels = [truncate([i if i !=pad_token else IGNORE_INDEX for i in example["label"]]) for example in list_data_dict]
        else:
            self.input_ids = [torch.tensor(example["input_ids"]) for example in list_data_dict if len(example["input_ids"]) < args.model_max_length]
            self.labels = [torch.tensor([i if i !=pad_token else IGNORE_INDEX for i in example["label"]])
                           for example in list_data_dict if len(example["input_ids"]) < args.model_max_length]
        print(f"Samples: {len(list_data_dict)} -> {len(self.input_ids)}")

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, i) -> Dict[str, torch.Tensor]:        
        return dict(input_ids=self.input_ids[i], labels=self.labels[i])


@dataclass
class DataCollatorForSupervisedDataset(object):
    """Collate examples for supervised fine-tuning."""

    tokenizer: transformers.PreTrainedTokenizer

    def __call__(self, instances: Sequence[Dict]) -> Dict[str, torch.Tensor]:
        input_ids, labels = tuple([instance[key] for instance in instances] for key in ("input_ids", "labels"))
        input_ids = torch.nn.utils.rnn.pad_sequence(
            input_ids, batch_first=True, padding_value=self.tokenizer.pad_token_id
        )
        labels = torch.nn.utils.rnn.pad_sequence(labels, batch_first=True, padding_value=IGNORE_INDEX)

        return dict(
            input_ids=input_ids,
            labels=labels,
            attention_mask=input_ids.ne(self.tokenizer.pad_token_id),
        )


def make_supervised_data_module(tokenizer: transformers.PreTrainedTokenizer, data_args) -> Dict:
    """Make dataset and collator for supervised fine-tuning."""
    train_dataset = SupervisedDataset(tokenizer=tokenizer, data_path=data_args.data_path, args=data_args)
    data_collator = DataCollatorForSupervisedDataset(tokenizer=tokenizer)
    return dict(train_dataset=train_dataset, eval_dataset=None, data_collator=data_collator)


def is_master():
    return not dist.is_available() or not dist.is_initialized() or dist.get_rank() == 0



class LoggingCallback(transformers.TrainerCallback):
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs is not None:
            log_message = {
                "loss": logs.get("loss", None),
                "learning_rate": logs.get("learning_rate", None),
                "epoch": logs.get("epoch", None),
                "step": state.global_step
            }
            output_log="seed-coder-training-log.jsonl"
            if is_master():
                if not os.path.exists(output_log):
                    with open(output_log, "w", encoding="utf-8") as f:
                        pass
                with open(output_log, "a",encoding="utf-8") as f:
                    import json
                    f.write(json.dumps(log_message)+"\n")
                print(log_message)

def train():
    parser = transformers.HfArgumentParser((ModelArguments, DataArguments, TrainingArguments))
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()
    print("data path:", data_args.data_path)
    print("output path:", training_args.output_dir)
    print("save_staps:",training_args.save_steps)
    args = {**model_args.__dict__, **data_args.__dict__, **training_args.__dict__}
    args = argparse.Namespace(**args)
    model = transformers.AutoModelForCausalLM.from_pretrained(
        model_args.model_name_or_path,
        device_map="auto",
        cache_dir=training_args.cache_dir,
        use_cache=False
    )
    tokenizer = transformers.AutoTokenizer.from_pretrained(
        model_args.model_name_or_path,
        truncation=True,
        padding_side="left",
        model_max_length = training_args.model_max_length,
    )
    data_module = make_supervised_data_module(tokenizer=tokenizer, data_args=args)
    trainer = Trainer(model=model, tokenizer=tokenizer, args=training_args, **data_module, callbacks=[LoggingCallback])
    trainer.train()
    trainer.save_model(output_dir=training_args.output_dir)

if __name__ == "__main__":
    train()