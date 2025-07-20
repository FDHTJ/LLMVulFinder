import argparse
import os.path
import random
import time

import requests
import json

from openai import OpenAI

from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_respond(prompt, model):
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
            if e.body["message"].find(
                    "The response was filtered due to the prompt triggering Azure OpenAI's content management policy.") != -1:
                return "Filtered by policy"
            time.sleep(2)
    return "network error"


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Analyze code vulnerabilities.')
    parser.add_argument('--model', type=str, default="o4-mini", help='Model name to use (e.g., gpt-4o)')

    parser.add_argument('--file', type=str, default="primevul_test.json", help='Input JSON file path')
    args = parser.parse_args()
    print(args.model)
    print(args.file)
    model = args.model
    file_name = args.file
    prompt_template = '''
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
    output_file = file_name.split(".")[0] + f"_{model}" + ".jsonl"
    print(output_file)
    if not os.path.exists(output_file):
        with open(output_file, mode='w') as f:
            pass
    with open(output_file, 'r', encoding='utf-8') as o:
        l = len(o.readlines())
    with (open(file_name, 'r', encoding='utf-8') as f,
          open(output_file, 'a', encoding='utf-8') as o, ):
        all_function = json.load(f)[l:]
        def process_item(d):
            respond1 = "network error"
            prompt = prompt_template.replace('<code>', d['func_before'] if 'func_before' in d.keys() else d[
                'func'] if 'func' in d.keys() else d['code'])
            while (respond1 == "network error"):
                respond1 = get_respond(prompt, model)
            d["respond_of_test"] = respond1.model_dump_json() if not isinstance(respond1,str) else respond1
            return d
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(process_item, d) for d in all_function ]
            for future in tqdm(as_completed(futures), total=len(futures)):
                result = future.result()
                o.write(json.dumps(result, ensure_ascii=False) + '\n')