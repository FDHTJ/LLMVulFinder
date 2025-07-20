import argparse
import json
import os
import random

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
parser.add_argument("--model_path", default='trained_qwen_2.5_coder-7B', type=str)
parser.add_argument("--method", default='for_reward_model', type=str)
parser.add_argument("--data_path", default='train_data_for_qwen_coder.json', type=str)
parser.add_argument("--batch_size", default=1, type=int)
parser.add_argument("--gpu", default=0, type=int)
parser.add_argument("--number_of_sentence", default=16, type=int)

args = parser.parse_args()
print(args.model_path)
print(args.data_path)
method=args.method
input_file=args.data_path
output_file=input_file.split(".")[0]+f"_{method}.jsonl"

if not os.path.exists(output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        pass
with open(output_file, 'r', encoding='utf-8') as f:
    l = len(f.readlines())
print("output_file:",output_file)
if l<20000:
    device = torch.device(f"cuda:{args.gpu}")
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_path,
        padding_side="left",
        trust_remote_code=True
    )

    model = AutoModelForCausalLM.from_pretrained(
        args.model_path,
        torch_dtype=torch.bfloat16
        # device_map="auto"
    )
    model.to(device)

    def form_prompt(code):
        prompt=f'''Code:
    
    {code}
    
    ---
    
    Instructions:
    
    You are given a code snippet. Your task is to analyze the code and determine if it contains any vulnerabilities. 
    
    Please respond in the following format:
    
    1.functional Analysis
    
        Neutrally describe what each part of the code is intended to do. Do not mention any issues or potential vulnerabilities.
    
    2. Vulnerability Analysis
    
        Based on the code’s behavior, explain what vulnerabilities the code is susceptible to, whether the code prevents these vulnerabilities from occurring, or whether the code actually contains these vulnerabilities. 
    
        - Don’t assume a flaw or the code is safe—verify and assess it logically
    3. Decision
    
        Yes/No,[summary of your analysis]'''
        return prompt
    def process_batch(batch):
        inputs = [
            tokenizer.apply_chat_template([
                {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
                {"role": "user", "content": form_prompt(item['code'] if "code" in item.keys() else item['func_before'])}
            ], add_generation_prompt=True, tokenize=False)
            for item in batch
        ]
        number_of_sentence=args.number_of_sentence

        inputs = tokenizer(
            inputs,
            return_tensors="pt",
            padding="longest",
            truncation=True,
            max_length=4096
        ).to(model.device)
        model.eval()

        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                max_new_tokens=1024,
                use_cache=True,
                do_sample=True,
                num_return_sequences=number_of_sentence,
                temperature=1.0
            )

        responds=[]
        for j in range(args.batch_size):
            respond=[]
            for i in range(number_of_sentence):
                temp=tokenizer.decode(outputs[j*number_of_sentence+i][len(inputs.input_ids[j]):], skip_special_tokens=True)
                respond.append(temp)
            responds.append(respond.copy())
        return responds


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
                item["respond_for_rm"] = item_responses
                result_file.write(json.dumps(item) + "\n")
            progress_bar.update(args.batch_size)
    progress_bar.close()