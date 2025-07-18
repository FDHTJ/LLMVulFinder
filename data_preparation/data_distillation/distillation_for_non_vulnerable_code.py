import argparse
import os.path
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import json
from openai import OpenAI

from tqdm import tqdm
def get_respond(prompt,model):
    client = OpenAI(
        base_url="your base url",
        api_key="your api key"
    )
    i = 0
    while (i < 3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    },
                ],
                max_tokens=10240
            )
            re = response.choices[0].message
            return re
        except Exception as e:
            i += 1
            if e.body["message"].find("The response was filtered due to the prompt triggering Azure OpenAI's content management policy.") !=-1:
                return "Filtered by policy"
            time.sleep(2)
    return "network error"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze code vulnerabilities.')
    parser.add_argument('--model', type=str, required=True, help='Model name to use (e.g., gpt-4o)')
    parser.add_argument('--file', type=str, required=True, help='Input file prefix')
    args = parser.parse_args()
    print(args.model)
    print(args.file)
    model = args.model
    file_name = args.file
    s="train_with_code_only"
    total=1000000
    with open("prompts.json",'r',encoding='utf-8') as f:
        prompts=json.load(f)
    prompts=prompts[s]
    if not os.path.exists(f"{s}/{file_name}_{model}.jsonl"):
        with open(f"{s}/{file_name}_{model}.jsonl",'w'):
            pass
    with open(f"{s}/{file_name}_{model}.jsonl", 'r', encoding='utf-8') as o:
        l=len(o.readlines())
    with (open(f"{file_name}.json", 'r', encoding='utf-8') as f,
          open(f"{s}/{file_name}_{model}.jsonl", 'a', encoding='utf-8') as o,):
        all_function = json.load(f)[l:total]
        def process_item(d):
            prompt = prompts["non_vulnerable_code"]
            respond1 = "network error"
            prompt = prompt.replace("<code>", d["func_before"])
            while (respond1 == "network error"):
                respond1 = get_respond(prompt, model)
            d["respond_before"] = respond1.model_dump_json() if not isinstance(respond1,str) else respond1
            return d
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(process_item, d) for d in all_function]
            for future in tqdm(as_completed(futures), total=len(futures)):
                result = future.result()
                o.write(json.dumps(result, ensure_ascii=False) + '\n')



