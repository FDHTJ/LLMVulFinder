import json
import os

import requests
import tqdm
from bs4 import BeautifulSoup


def get_cwe_description(data_path):
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        all_results = []
        "https://cwe.mitre.org/data/definitions/787.html"
        for d in tqdm.tqdm(data):
            id=d.split('-')[-1]
            url=f"https://cwe.mitre.org/data/definitions/{id}.html"
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                description=soup.find("div", {"class":"detail"})
                description=description.text.replace("\n"," ").strip()
                all_results.append({'cwe_id':d,'description':description})
            else:
                all_results.append({'cwe_id':d,'description':""})
                print(d)
        with open('cwe_description.json', 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=4)

def get_all_cve_description(data_file):
    with open(data_file,'r', encoding='utf-8') as f:
        all_data=json.load(f)
        processed_data=[]
        all_cwe=[]
        for d in all_data:
            if len(d["cwe_ids"])==0:continue
            if len(d["cwe_ids"])!=1:print(len(d["cwe_ids"]))
            processed_data.append({"cve_id":d["cve_id"],
                                   "cwe_ids":d["cwe_ids"],
                                   "cve_description":d["description"]})
            for i in d["cwe_ids"]:
                if i not in all_cwe:
                    all_cwe.append(i)
    with open("cve_id_and_description.json",'w', encoding='utf-8') as f:
        json.dump(processed_data,f,ensure_ascii=False,indent=4)
    with open("cwe_ids.json",'w', encoding='utf-8') as f:
        json.dump(all_cwe,f,ensure_ascii=False,indent=4)
def get_filted_cve(data_file):
    #cves that already contained in bigvul

    with open("cve_ids_already.json",'r', encoding='utf-8') as f:
        cve_id_already = json.load(f)
    with open("cwe_description.json",'r', encoding='utf-8') as f:
        cwe_description = json.load(f)
        temp={}
        for i in cwe_description:
            temp[i["cwe_id"]]=i["description"]
        cwe_description=temp
    with open(data_file,'r', encoding='utf-8') as f:
        processed_data=[]
        all_data=json.load(f)
        for d in tqdm.tqdm(all_data):
            if d["cve_id"] in cve_id_already: continue
            d["cwe_ids"]=[{"cwe_id":i,"cwe_description":cwe_description[i]} for i in d["cwe_ids"] if i !="CWE-Other"]
            if len(d["cwe_ids"])==0:continue
            processed_data.append(d)
    with open("final_cve_id_and_description.json",'w', encoding='utf-8') as f:
        json.dump(processed_data,f,ensure_ascii=False,indent=4)
def check_function_body(code:str):
    pre_brace = code.find('{')
    if pre_brace == -1:
        return False
    last_brace = len(code) - 1
    while last_brace >= 0:
        if code[last_brace] == '}':
            break
        last_brace -= 1
    if last_brace == -1:
        return False
    content = code[pre_brace + 1:last_brace].strip()
    if content == "":
        return False
    return True
def get_all_vul_data(data_file):
    #cves that already contained in bigvul
    with open("final_cve_id_and_description.json",'r', encoding='utf-8') as f:
        information=json.load(f)
        temp={}
        for i in information:
            temp[i["cve_id"]]=i
        information=temp
    indexes={}
    with open(data_file,'r', encoding='utf-8') as f:
        processed_data=[]
        all_data=json.load(f)
        for d in tqdm.tqdm(all_data):
            if not d["is_vul"]:continue
            if d["cve_id"] not in information.keys():
                continue
            if not (check_function_body(d["func_before"]) and check_function_body(d["func"])):
                continue
            if d["cve_id"] not in indexes.keys():
                indexes[d["cve_id"]]=0
            else:
                indexes[d["cve_id"]]+=1
            assert d["is_vul"]
            temp=d["cve_id"]
            d.pop("cve_id")
            d.pop("cwe_ids")
            processed_data.append({**information[temp],
                                   **d})
        with open("all_vul_data_megavul_left_by_bigvul_all_information.json", 'w', encoding='utf-8') as f:
            json.dump(processed_data,f,ensure_ascii=False,indent=4)

if __name__ == '__main__':
    get_all_vul_data("megavul_simple.json")
