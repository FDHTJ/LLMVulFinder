import argparse
import os.path
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import json

from openai import OpenAI

from tqdm import tqdm
def get_result_gpt(response:str):
    index=response.lower().find("decision")
    re=response[index:].lower()
    if re.find("yes")!=-1:
        return 1
    elif re.find("no")!=-1:
        return 0
    else:return -1
def get_respond(prompt,model):
    client = OpenAI(
        base_url="your base url",
        api_key="your api key",
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
    parser.add_argument('--file', type=str, required=True, help='Input JSON file path')
    args = parser.parse_args()
    print(args.model)
    print(args.file)
    model = args.model
    file_name = args.file
    prompt_template = """
Code:

```
<code>
       
```

CVE description:

<cve_description>      

Instruction:

The vulnerability of code refers to weaknesses or flaws that can be exploited by attackers to compromise the security of a system. Each code with vulnerability usually has a corresponding CVE(**Common Vulnerabilities and Exposures**) description. Each CVE provides a standardized way to identify, describe, and catalog publicly disclosed security vulnerabilities and exposures. A CVE entry contains a unique identifier for a specific vulnerability, along with a description that outlines the nature of the issue, its impact, and other relevant details. Based on the code and CVE description provided, analyze whether the code contains the vulnerability described in the CVE. If the provided code includes a fix for the vulnerability described in the CVE, it should be considered non-vulnerable. Please think this step by step and provide your answer in the following format:
Analysis:[Analyze the relationship between CVE and code step by step]
Decision:[Yes(vulnerable)/No(non-vulnerable) based on the above analysis ]
"""
    output_file = file_name.split(".")[0] + f"_{model}" + ".jsonl"
    print(output_file)
    if not os.path.exists(output_file):
        with open(output_file, mode='w',encoding='utf-8') as f:
            pass
    with open(output_file, 'r', encoding='utf-8') as o:
        l = len(o.readlines())
    with (open(file_name, 'r', encoding='utf-8') as f,
          open(output_file, 'a', encoding='utf-8') as o, ):
        all_function = json.load(f)[l:]
        def process_item(d):

            prompt = prompt_template.replace('<code>', d['func_after'])
            prompt = prompt.replace("<cve_description>", d["cve_description"])
            respond2 = "network error"
            while respond2 == "network error":
                respond2 = get_respond(prompt, model)
            d["respond_after"] = respond2.model_dump_json() if not isinstance(respond2, str) else respond2
            #If the model judge the patched code is vulnerable, then it is no need to judge vulnerable code
            if isinstance(respond2, str) or get_result_gpt(json.loads(d["respond_after"])["content"]) != 0:
                return d

            prompt = prompt_template.replace('<code>', d['func_before'])
            prompt = prompt.replace("<cve_description>", d["cve_description"])
            respond1 = "network error"
            while respond1 == "network error":
                respond1 = get_respond(prompt, model)
            d["respond_before"] = respond1.model_dump_json() if not isinstance(respond1, str) else respond1

            return d
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(process_item, d) for d in all_function]
            for future in tqdm(as_completed(futures), total=len(futures)):
                result = future.result()
                o.write(json.dumps(result, ensure_ascii=False) + '\n')
