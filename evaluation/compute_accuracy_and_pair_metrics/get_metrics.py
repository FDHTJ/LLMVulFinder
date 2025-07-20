import argparse
import json
import os

def get_result_gpt(response:str):
    index=response.lower().find("decision")
    re=response[index:].lower()
    if re.find("yes")!=-1:
        return 1
    elif re.find("no")!=-1:
        return 0
    else:return -1

def get_metrics(data_file,is_GPT=False):

    print(data_file)
    accuracy={'before':[0,0],
    'after':[0,0],
    'non':[0,0],
    }
    count=0
    pair_result={}
    if not os.path.exists(data_file):
        return (0,0)
    with open(data_file, 'r',encoding="utf-8") as f:
        datas=f.readlines()
        if not is_GPT and data_file.find("primevul") != -1:
            with open("results/primevul.json",'r',encoding="utf-8") as f:
                already_functions=[d["func_before"] for d in json.load(f)]
            datas=[d for d in datas if json.loads(d)["func_before"] in already_functions]
        for d in datas:
            d=json.loads(d)
            accuracy[d["type"]][1]+=1
            p=get_result_gpt(d['respond_of_test'] if not is_GPT else json.loads(d['respond_of_test'])["content"] if d['respond_of_test'] !='Filtered by policy' else d['respond_of_test'])
            if p==-1:
                count+=1
            p=p if p!=-1 else 0
            if p==d["target"]:
                accuracy[d["type"]][0] += 1
            if d["type"] !="non":
                if d["pair_index"] not in pair_result.keys():
                    pair_result[d["pair_index"]]={"before":-1,"after":-1}
                pair_result[d["pair_index"]][d["type"]]=p
    for key in accuracy.keys():
        print(f"Accuracy {key}:",accuracy[key][0]/accuracy[key][1])
    before=accuracy["before"][0]/accuracy["before"][1]
    after=accuracy["after"][0]/accuracy["after"][1]
    non=accuracy["non"][0]/accuracy["non"][1]
    bm1=3*3/(1/((1/3)*before)+1/((1/3)*after)+1/((1/3)*non))
    bm2=3*(before*after*non)/(before*after+after*non+before*non)
    print("BM1:",bm1)
    pair_metric = [0, 0, 0, 0]
    '''
        0:before=0 after=0 P-B
        1:before=0 after=1 P-R
        2:before=1 after=0 P-C
        3:before=1 after=1 P-V
    '''
    error=0
    for key, value in pair_result.items():
        if value["before"] == -1 or value["after"] == -1:
            error+=1
            continue
        index = value["before"] * 2 + value["after"]
        pair_metric[index] += 1
    total_pair = sum(pair_metric)
    pair_metric=[i/total_pair for i in pair_metric]
    print(f"P-C {pair_metric[2]:.4f}\n")
    print(f"P-V: {pair_metric[3]:.4f}\n")
    print(f"P-B: {pair_metric[0]:.4f}\n")
    print(f"P-R: {pair_metric[1]:.4f}\n")
def get_token_cost(data_file,is_GPT=False):
    import transformers
    tokenizer=transformers.AutoTokenizer.from_pretrained("Qwen/Qwen2.5-Coder-7B-Instruct",
                                                         pad_token='<|extra_0|>',
                                                         eos_token='<|im_end|>',
                                                         cache_dir=None,
                                                         truncation=True,
                                                         padding_side="right",
                                                         trust_remote_code=True
                                                         )
    tokenizer.add_special_tokens({"additional_special_tokens": ["<|im_end|>", "<|im_start|>"]})
    print(data_file)
    accuracy={'before':[0,0],
    'after':[0,0],
    'non':[0,0],
    }
    if not os.path.exists(data_file):
        return (0,0)
    with open(data_file, 'r',encoding="utf-8") as f:
        datas=f.readlines()
        for d in datas:

            d=json.loads(d)
            if d['respond_of_test'] == 'Filtered by policy':
                continue
            accuracy[d["type"]][1]+=1
            p=len(tokenizer.encode(d['respond_of_test'] if not is_GPT else json.loads(d['respond_of_test'])["content"] if d['respond_of_test'] !='Filtered by policy' else d['respond_of_test']))
            accuracy[d["type"]][0] += p
    total=0
    total_number=0
    for key in accuracy.keys():
        total+=accuracy[key][0]
        total_number+=accuracy[key][1]
        print(f"Token Cost {key}:",accuracy[key][0]/accuracy[key][1])

    print("over all average:",total/total_number)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Get Metrics')
    parser.add_argument('--model', type=str, default="qwen-2.5-coder-trained", help='model of respond')

    parser.add_argument('--type', type=str, default="primevul", help='our or primevul')
    args = parser.parse_args()
    is_gpt=(args.model.find("gpt")!=-1 or args.model.find("mini") !=-1)
    get_metrics(f"results/{args.type}_test_{args.model}.jsonl",is_gpt)
    get_token_cost(f"results/{args.type}_test_{args.model}.jsonl",is_gpt)