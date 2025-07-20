import argparse
import json
import os
import random

import transformers
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


def read_file(path):
    with open(path, 'r') as f:
        return json.load(f)


def batch_generator(data, batch_size):
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]


parser = argparse.ArgumentParser()
parser.add_argument("--model_path",
                    default='output/star-coder2/checkpoint-400',
                    type=str)
parser.add_argument("--method", default='star-coder2_trained', type=str)
parser.add_argument("--data_path",
                    default='test_data/our_test.json',
                    type=str)
parser.add_argument("--batch_size", default=16, type=int)
parser.add_argument("--gpu", default=0, type=int)
args = parser.parse_args()
print(args.model_path)
print(args.data_path)
method = args.method
input_file = args.data_path
output_file = input_file.split(".")[0] + f"_{method}.jsonl"

if not os.path.exists(output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        pass
with open(output_file, 'r', encoding='utf-8') as f:
    l = len(f.readlines())
print("output_file:", output_file)
if l < 1500:
    device = torch.device(f"cuda:{args.gpu}")
    model = transformers.AutoModelForCausalLM.from_pretrained(
        args.model_path,

    )
    tokenizer = transformers.AutoTokenizer.from_pretrained(
        args.model_path,
        truncation=True,
        padding_side="left",
        model_max_length=4096,
    )
    tokenizer.pad_token = tokenizer.eos_token
    print( tokenizer.eos_token)
    model.to(device)


    def form_prompt(code):
        prompt = '''
Code:

<code>

---

Instructions:
You are given a code snippet. Your task is to analyze the code and determine if it contains any vulnerabilities.
Please respond in the following format:
1.Functional Analysis
    Neutrally describe what each part of the code is intended to do. Do not mention any issues or potential vulnerabilities.
2. Vulnerability Analysis
    Based on the code’s behavior, explain what vulnerabilities the code is susceptible to, whether the code prevents these vulnerabilities from occurring, or whether the code actually contains these vulnerabilities.
    - Don’t assume a flaw or the code is safe—verify and assess it logically
3. Decision
    Yes,the code contains vulnerability./No,the code dose not contain any vulnerabilities.[summary of your analysis]
    '''
        return prompt.replace("<code>",code)


    def chatml_format_preprocess(sources, tokenizer):
        roles = {"user": "<[begin▁of▁sentence]>user\n", "assistant": "<[begin▁of▁sentence]>assistant\n",
                 "system": "<[begin▁of▁sentence]>system\n"}

        sentence_end = "<[end▁of▁sentence]>"

        input_id=""
        for j, sentence in enumerate(sources):
            role = roles.get(sentence["role"])
            if not role:
                raise ValueError(f"Unknown role '{sentence['role']}' encountered.")

            _input_id = role + sentence["content"] +sentence_end
            input_id += _input_id
        input_id+=roles["assistant"]
        return input_id
    def process_batch(batch):
        inputs = [
            chatml_format_preprocess([
                {"role": "system",
                 "content": "You are StarCoder2. You are a helpful assistant."},
                 {"role": "user", "content": form_prompt(item['code'] if "code" in item.keys() else item['func_before'])}
            ],tokenizer=tokenizer)
            for item in batch
        ]


        inputs = tokenizer(
            inputs,
            return_tensors="pt",
            padding="longest",
            truncation=True,
            add_special_tokens=False,
            max_length=4096
        ).to(model.device)
        model.eval()
        # inputs.pop("token_type_ids")
        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                max_new_tokens=1024,
                use_cache=True,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.encode("<[end▁of▁sentence]>",add_special_tokens=False)[0]
            )

        batch_responses = []
        for i in range(len(batch)):
            sample_outputs = outputs[i]

            decoded_responses = [
                tokenizer.decode(sample_outputs[len(inputs.input_ids[i]):], skip_special_tokens=True)
            ]
            batch_responses.append(decoded_responses)

        return batch_responses


    # test_data = read_file(args.data_path)

    with open(input_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)[l:]
    random.seed(42)
    print(len(test_data))
    progress_bar = tqdm(total=len(test_data), desc=f"Processing items {output_file.split('/')[-1]}")

    with open(output_file, "a+") as result_file:
        for batch in batch_generator(test_data, args.batch_size):
            responses = process_batch(batch)
            for item, item_responses in zip(batch, responses):
                assert len(item_responses) == 1
                item["respond_of_test"] = item_responses[0]
                result_file.write(json.dumps(item) + "\n")
            progress_bar.update(len(batch))

    progress_bar.close()