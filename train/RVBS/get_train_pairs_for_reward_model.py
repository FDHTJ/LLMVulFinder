import json
import random


def get_result_gpt(response:str):
    index=response.lower().find("decision")
    re=response[index:].lower()
    if re.find("yes")!=-1:
        return 1
    elif re.find("no")!=-1:
        return 0
    else:return -1

def get_pairs(d):
    target=d["target"]
    yes=[]
    no=[]
    pairs=[]
    for i in d["respond"]:
        p=get_result_gpt(i)
        if p==1:yes.append(i)
        elif p==0:no.append(i)
        else:print(i)
    if len(yes)==0:return []
    if len(no)==0:return []
    temp_length=min(len(yes),len(no))
    for i in range(temp_length):
        pairs.append({"func_before":d["func_before"],"target":target,"yes":yes[i],"no":no[i]})
    for i in range(temp_length,len(no)):
        j=random.randint(0,len(yes)-1)
        pairs.append({"func_before":d["func_before"],"target":target,"yes":yes[j],"no":no[i]})
    for i in range(temp_length,len(yes)):
        j=random.randint(0,len(no)-1)
        pairs.append({"func_before":d["func_before"],"target":target,"yes":yes[i],"no":no[j]})
    return pairs

with open("train_data_for_qwen_coder_for_reward_model.jsonl",'r',encoding='utf-8') as f:
    datas=f.readlines()
    datas=[json.loads(d) for d in datas]
    results=[]
    for d in datas:
        temp=get_pairs(d)
        if len(temp)!=0:
            target=temp[0]["target"]
            for t in temp:
                if target:
                    t["chosen"]=t.pop("yes")
                    t["rejected"]=t.pop("no")
                else:
                    t["chosen"] = t.pop("no")
                    t["rejected"] = t.pop("yes")
with open("train_data_for_qwen_coder_pairs_for_reward_model.jsonl",'w',encoding='utf-8') as f:
    json.dump(results,f,ensure_ascii=False,indent=4)