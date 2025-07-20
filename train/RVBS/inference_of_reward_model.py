import argparse
import json
import re, ast
from transformers import AutoTokenizer, pipeline, AutoModelForSequenceClassification
import torch
from tqdm import tqdm
parser = argparse.ArgumentParser()
parser.add_argument("--model_path", default='checkpoint-1600', type=str)
parser.add_argument("--data_path", default='train_for_random_forest.jsonl', type=str)
parser.add_argument("--gpu",default='0', type=str)
args = parser.parse_args()
print("model path :",args.model_path)
print("data_path :",args.data_path)
if args.data_path.endswith('.jsonl'):
    output_file=args.data_path.replace(".jsonl",f"_{args.model_path}.jsonl")
else:
    output_file=args.data_path.replace(".json",f"_{args.model_path}.json")
print("output file :",output_file)

def read_file_jsonl(path):
    '''
    Reads a JSON file where each line is a separate JSON object.

    Args:
        path (str): The file path to the JSON file to be read.

    Returns:
        list: A list of dictionaries parsed from the JSON objects in the file.
    '''
    data = []
    with open(path, 'r') as r:
        lines = r.readlines()
        for l in lines:
            item = json.loads(l)
            data.append(item)
    return data
def read_file(path):
    return json.load(open(path))


tokenizer = AutoTokenizer.from_pretrained(args.model_path)
# tokenizer.padding_side = "left"
tokenizer.model_max_length = 4096
device = torch.device(f"cuda:{args.gpu}")  # accelerator.device
rm_pipe = pipeline(
    "sentiment-analysis",
    model=args.model_path,
    # device="auto",
    device=device,
    tokenizer=tokenizer,
    model_kwargs={"torch_dtype": torch.bfloat16}
)


pipe_kwargs = {
    "return_all_scores": True,
    "function_to_apply": "none",
    "batch_size": 1
}
if args.data_path.endswith(".jsonl"):
    data=read_file_jsonl(args.data_path)
else:
    data = read_file(args.data_path)
with open(output_file,'w')as w:

    for data_item in tqdm(data):
        code=data_item['func_before']
        prompt=f'''Code:

{code}

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
        answers=[]
        for response in data_item['respond']:
            answers.append(response)
        texts = []
        for answer in answers:
            text = [
                {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": answer}
            ]
            texts.append(text)
        test_texts = [tokenizer.apply_chat_template(text, tokenize=False, add_generation_prompt=False) for text in
                          texts]
        # outputs=
        pipe_outputs = rm_pipe(test_texts, **pipe_kwargs)
        rewards = [output[0]["score"] for output in pipe_outputs]
        print(rewards)

        data_item['rewards']=rewards
        w.write(json.dumps(data_item)+'\n')
    print(len(data))
