import pandas as pd
import json
def calculate_metrics(test_more,prefix):
    type=test_more["type"]
    pair_index=test_more["pair_index"]
    pred=test_more["pred"]
    before=0
    true_before=0
    after=0
    true_after=0
    non=0
    true_non=0
    pair_result={}
    for i in range(len(type)):
        t=type[i]
        p=pair_index[i]
        pr=pred[i]
        if p!=-1:
            if p not in pair_result.keys():
                pair_result[p]={"before":None,"after":None}
            pair_result[p][t]=pr
        if t=="before":
            before+=1
            if pr==1:
                true_before+=1
        elif t=="after":
            after+=1
            if pr==0:
                true_after+=1
        else:
            non+=1
            if pr==0:
                true_non+=1
    pair_metric=[0,0,0,0]
    '''
        0:代表before=0 after=0 P-B
        1:代表before=0 after=1 P-R
        2:代表before=1 after=0 P-C
        3:代表before=1 after=1 P-V
    '''
    for key,value in pair_result.items():
        # if value["before"]==None or value["after"]==None:continue
        assert value["before"]!=None and value["after"]!=None
        index=value["before"]*2+value["after"]
        pair_metric[index]+=1
    total_pair=sum(pair_metric)
    pair_metric=[i/total_pair*100 for i in pair_metric]
    print(f"{prefix} Before Accuracy: {true_before/before*100:.4f}\n")
    print(f"{prefix} After Accuracy: {true_after/after*100:.4f}\n")
    print(f"{prefix} Non-vul Accuracy: {true_non/non*100:.4f}\n")
    before = true_before/before
    after = true_after/after
    non = true_non/non
    bm1 = 3 / (1 / ((1 / 3) * before) + 1 / ((1 / 3) * after) + 1 / ((1 / 3) * non))
    bm2 = (before * after * non) / (before * after + after * non + before * non)
    print("BM:", bm1)
    print("BM1:", bm2)
    print(f"{prefix} P-C {pair_metric[2]:.4f}\n")
    print(f"{prefix} P-V: {pair_metric[3]:.4f}\n")
    print(f"{prefix} P-B: {pair_metric[0]:.4f}\n")
    print(f"{prefix} P-R: {pair_metric[1]:.4f}\n")
    print("\n")
def get_pair_metric(result_file,test_data_file="../Database/SVulD/primevul_test_for_pretrain.jsonl"):
    result=pd.read_csv(result_file)
    result=result['pred'].tolist()
    datas=[0]*len(result)
    with open(test_data_file,'r') as f:
        for line in f.readlines():
            data=json.loads(line)
            data["pred"]=1 if result[data["index"]] else 0
            datas[data["index"]]=data
        test_more={"type":[d["type"] for d in datas],"pair_index":[d["pair_index"] for d in datas],"pred":[d["pred"] for d in datas]}

    calculate_metrics(test_more,"SVulD")
get_pair_metric("LineVul/linevul/detect_primevul.csv")
get_pair_metric("SVulD/detect_primevul.csv")
