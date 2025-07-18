from random import randint
import random
# import pandas as pd
import json

import pandas as pd
import tqdm
from cmath import isnan
import numpy as np
def get_all_vul_data(data_path,save_file):
    with open(data_path,'r',encoding="utf-8") as f:
        all_data = json.load(f)
    all_vul_data=[]
    for (index,d) in tqdm.tqdm( all_data.items()):
        if d['vul']=="1":
            all_vul_data.append({
                "cve_id":d['CVE ID'],
                "cve_description":d['Summary'],
                "cwe_id":d['CWE ID'],
                "func_before":d["func_before"],
                "func_after":d["func_after"],
                "code_link":d["codeLink"] if "codeLink" in d.keys() else "",
                "lang":d["lang"],
                "project":d["project"],
                "project_before":d["project_before"],
                "project_after":d["project_after"],
            })
    with open(save_file, 'w',encoding="utf-8") as outfile:
        json.dump(all_vul_data, outfile,indent=4,ensure_ascii=False)
def get_all_non_vul_data(data_path,save_file):
    with open(data_path,'r',encoding='utf-8') as infile:
        all_data=json.load(infile)
        all_non_vul_data=[]
        for key, d in all_data.items():
            if d['vul'] == "0":
                all_non_vul_data.append({
                    "cve_id": d['CVE ID'],
                    "cve_description": d['Summary'],
                    "cwe_id": d['CWE ID'],
                    "func_before": d["func_before"],
                    "func_after": d["func_after"],
                    "code_link": d["codeLink"] if "codeLink" in d.keys() else "",
                    "lang": d["lang"],
                    "project": d["project"],
                    "project_before": d["project_before"],
                    "project_after": d["project_after"],
                })
        with open(save_file, 'w', encoding='utf-8') as outfile:
            json.dump(all_non_vul_data, outfile, indent=4, ensure_ascii=False)
def get_non_vul_data_for_data_distillation(data_path,save_file,number):
    def contain_method(code):
        left=code.find("{")
        i=len(code)-1
        while i>=0:
            if code[i]=='}':
                break
            else:
                i-=1

        if left==-1 or i==-1:
            return False
        code=code[left+1:i]
        if code.strip()=="":
            return False
        return True
    with open(data_path,'r',encoding='utf-8') as infile:
        all_data=json.load(infile)
        all_processd_non_vul_data=[]
        for d in all_data:
            if d["cve_id"]=="":
                continue
            if contain_method(d["func_before"]):
                all_processd_non_vul_data.append(d)
        random.shuffle(all_processd_non_vul_data)
    all_processd_non_vul_data=all_processd_non_vul_data[:number]
    with open(save_file,'w',encoding='utf-8') as outfile:
        json.dump(all_processd_non_vul_data, outfile, indent=4, ensure_ascii=False)
if __name__ == '__main__':
    get_all_vul_data("MSR_data_cleaned.json","all_vul_data.json")
    get_all_non_vul_data("MSR_data_cleaned.json","all_non_vul_data.json")
