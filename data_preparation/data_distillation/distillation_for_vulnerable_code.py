import argparse
import os
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
            time.sleep(2)
    return "network error"
def get_out_of_comment(ls):
    i=0
    process=[]
    while i < len(ls):
        l=ls[i]["content"] if "content" in ls[i].keys() else ls[i]["original_content"]
        if l.find("/*")!=-1 and l.find("*/")!=-1:
            l=l[:l.find("/*")].strip()
            if l!="":
                print(ls[i])

                process.append(ls[i])
        elif l.find("/*")!=-1:
            l = l[:l.find("/*")].strip()
            if l!="":
                print(ls[i])
                process.append(ls[i])
            i+=1
            while i<len(ls) and (ls[i]["content"] if "content" in ls[i].keys() else ls[i]["original_content"]).find("*/")==-1:
                i+=1
            if i<len(ls):
                l=ls[i]["content"] if "content" in ls[i].keys() else ls[i]["original_content"]
                l=l[l.find("*/")+2:].strip()
                if l!="":
                    print(ls[i])
                    process.append(ls[i])
        elif not l.startswith("//"):
            process.append(ls[i])
        i+=1
    return process
def get_vulnerable_lines(d):
    #The diffs can be obtained by get_diff.py
    ls=[]
    for k,v in d["diffs"].items():
        for l in v:
            ls.append(l)
    ls=sorted(ls,key=lambda x:x["line_number"])
    ls_no_comment=get_out_of_comment(ls)
    ls=[f"Line {x['line_number']}: {x['original_content'] if 'original_content' in x.keys() else x['content']}"  for x in ls_no_comment]
    return "\n".join(ls)
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
            prompt = prompts["vulnerable_code"]
            respond1 = "network error"
            prompt = prompt.replace("<code>", d["func_before"])
            prompt = prompt.replace("<cwe_description>", d["cwe_description"])
            prompt = prompt.replace("<cve_description>", d["cve_description"])
            prompt = prompt.replace("<vulnerable_lines>", get_vulnerable_lines(d))
            while (respond1 == "network error"):
                respond1 = get_respond(prompt, model)
            d["respond_before"] = respond1.model_dump_json()
            return d
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(process_item, d) for d in all_function]
            for future in tqdm(as_completed(futures), total=len(futures)):
                result = future.result()
                o.write(json.dumps(result, ensure_ascii=False) + '\n')








