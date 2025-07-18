import json
import tqdm


def get_train_for_qwen_coder(data_file):
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
    with open(data_file.replace(".json",".jsonl"), "w", encoding="utf-8") as f:
        pass
    with (open(data_file, "r", encoding="utf-8") as f,
          open(data_file.replace(".json",".jsonl"), "a", encoding="utf-8") as o):
        data = json.load(f)
        print("loading data:",len(data))
        for d in data:
            code_key = "func_before" if "func_before" in d else "code"
            temp = {
                "messages": [
                    {"role": "system",
                     "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
                    {"role": "user", "content": f"{prompt.replace('<code>', d[code_key])}"},
                    {"role": "assistant", "content": f"{d['respond_before']}"},
                ],
                "format": "chatml"
            }
            o.write(json.dumps(temp, ensure_ascii=False) + '\n')
    with open(data_file.replace(".json",".jsonl"), "r", encoding="utf-8") as f:
        l=len(f.readlines())
def get_train_for_seed_coder(data_file):
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
    with open(data_file.replace(".json",".jsonl"), "w", encoding="utf-8") as f:
        pass
    with (open(data_file, "r", encoding="utf-8") as f,
          open(data_file.replace(".json",".jsonl"), "a", encoding="utf-8") as o):
        data = json.load(f)
        print("loading data:",len(data))
        for d in data:
            code_key = "func_before" if "func_before" in d else "code"
            temp = {
                "messages": [
                    {"role": "system",
                     "content": "You are an AI programming assistant, utilizing the Seed-Coder model, developed by ByteDance Seed, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer.\n\n"},
                    {"role": "user", "content": f"{prompt.replace('<code>', d[code_key])}"},
                    {"role": "assistant", "content": f"{d['respond_before']}"},
                ],
                "format": "chatml"
            }
            o.write(json.dumps(temp, ensure_ascii=False) + '\n')
    with open(data_file.replace(".json",".jsonl"), "r", encoding="utf-8") as f:
        l=len(f.readlines())
def get_train_for_star_coder(data_file):
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
    with open(data_file.replace(".json",".jsonl"), "w", encoding="utf-8") as f:
        pass
    with (open(data_file, "r", encoding="utf-8") as f,
          open(data_file.replace(".json",".jsonl"), "a", encoding="utf-8") as o):
        data = json.load(f)
        print("loading data:",len(data))
        count=0
        for d in data:
            code_key = "func_before" if "func_before" in d else "code"
            temp = {
                "messages": [
                    {"role": "system",
                     "content": "You are StarCoder2. You are a helpful assistant."},
                    {"role": "user", "content": f"{prompt.replace('<code>', d[code_key])}"},
                    {"role": "assistant", "content": f"{d['respond_before']}"},
                ],
                "format": "chatml"
            }
            o.write(json.dumps(temp, ensure_ascii=False) + '\n')
    with open(data_file.replace(".json",".jsonl"), "r", encoding="utf-8") as f:
        l=len(f.readlines())
if __name__=="__main__":
    get_train_for_qwen_coder("before_after_non_for_qwen_coder.json")
