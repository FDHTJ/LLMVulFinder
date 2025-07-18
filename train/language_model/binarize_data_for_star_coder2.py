import os
import numpy as np
import transformers
import tqdm
import sys
from typing import Dict
import argparse
import itertools
import json
from utils import utils
def chatml_format_preprocess(sources, tokenizer: transformers.PreTrainedTokenizer, max_len: int, system_message: str = "You are a helpful assistant.", only_last_turn_loss=False) -> Dict:
    IGNORE_INDEX = -100
    roles = {"user": "<[begin▁of▁sentence]>user\n", "assistant": "<[begin▁of▁sentence]>assistant\n","system":"<[begin▁of▁sentence]>system\n"}

    
    sentence_start = tokenizer("<[begin▁of▁sentence]>",add_special_tokens=False).input_ids[0]
    sentence_end = tokenizer("<[end▁of▁sentence]>",add_special_tokens=False).input_ids[0]

    input_id, target, test_input_ids = [], [], []
    for j, sentence in enumerate(sources):
        role = roles.get(sentence["role"])
        if not role:
            raise ValueError(f"Unknown role '{sentence['role']}' encountered.")
        
        _input_id = tokenizer(role,add_special_tokens=False).input_ids + tokenizer(sentence["content"], add_special_tokens=False).input_ids+[sentence_end]
        input_id += _input_id

        if role=="<[begin▁of▁sentence]>system\n" or role == '<[begin▁of▁sentence]>user\n' or (only_last_turn_loss and j < len(sources) - 1):
            _target = [IGNORE_INDEX] * (len(_input_id))
        elif role == '<[begin▁of▁sentence]>assistant\n':
            _target = [IGNORE_INDEX] * len(tokenizer(role,add_special_tokens=False).input_ids) + _input_id[len(tokenizer(role,add_special_tokens=False).input_ids) :]
        else:
            raise NotImplementedError(f"Role '{role}' is not implemented.")
        
        target += _target

        if j == len(sources) - 1:
            test_input_ids += tokenizer(role).input_ids
        else:
            test_input_ids += _input_id
    assert len(input_id) == len(target), "Final input and target lengths do not match."
    return dict(
        test_input_ids=test_input_ids,
        input_ids=input_id,
        label=target,
    )


def read_file_from_position_with_chatml_format_processor(args):
    filename, start_position, end_position, worker_id, args = args
    tokenizer = args["tokenizer"]
    max_len = args["max_len"]
    objs = []
    with open(filename, 'r', encoding='utf-8', errors='replace') as f:  # Using 'replace' to handle errors better
        current_position = utils.find_next_line(f, start_position)
        f.seek(current_position)
        if current_position >= end_position:
            print(f"worker_id {worker_id} completed")
            return objs
        for cnt in tqdm.tqdm(itertools.count(), position=worker_id, desc=f"worker_id: {worker_id}"):
            line = f.readline()
            if not line:
                break
            obj = json.loads(line)
            obj = chatml_format_preprocess(
                obj["messages"], tokenizer, max_len=max_len, 
                only_last_turn_loss=obj.get("only_last_turn_loss", True)
            )
            objs.append(obj)
            if f.tell() >= end_position:
                break
    print(f"worker_id {worker_id} completed")
    return objs


def tokenize_file(workers=64, chunk_size=10000, input_path="./raw/sft.jsonl", output_path="./processed/sft.jsonl", tokenizer=None, max_len=32768):
    output_objs = utils.multi_tasks_from_file(input_path, workers=workers, task=read_file_from_position_with_chatml_format_processor, chunk_size=chunk_size, args={"tokenizer": tokenizer, "max_len": max_len})
    utils.write_jsonl_file(output_objs, output_path)
    np.save(f"{output_path}.npy", output_objs, allow_pickle=True)
    print(f"Successfully saved to {output_path}.npy")


def parse_args():
    parser = argparse.ArgumentParser(description='Argument Parser Example')
    parser.add_argument('--input_path', '-input_path', type=str, default="bigvul_before_after_non_for_star_coder2.jsonl", help='Path to input file')
    parser.add_argument('--output_path', '-output_path', type=str, default="processed_bigvul_before_after_non_for_star_coder2.jsonl", help='Path to output file')
    parser.add_argument('--workers', '-workers', type=int, default=8, help='Number of workers')
    parser.add_argument('--chunk_size', '-chunk_size', type=int, default=10240, help='Chunk size for file processing')
    parser.add_argument('--max_len', '-max_len', type=int, default=32768, help='Maximum length for tokenization')
    parser.add_argument('--tokenizer_path', '-tokenizer_path', type=str, default="star-coder-2-7B", help='Path to tokenizer')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(args.input_path)
    print(args.tokenizer_path)
    print(args.output_path)
    tokenizer = transformers.AutoTokenizer.from_pretrained(
        args.tokenizer_path,
        model_max_length=8192 * 4,
        truncation=True,
        padding_side="left",
        trust_remote_code=True
    )
    tokenizer.add_special_tokens({
        "additional_special_tokens": [
            "<[begin▁of▁sentence]>","<[end▁of▁sentence]>"
        ]})
    tokenize_file(workers=args.workers, chunk_size=args.chunk_size, input_path=args.input_path, output_path=args.output_path, tokenizer=tokenizer, max_len=args.max_len)
