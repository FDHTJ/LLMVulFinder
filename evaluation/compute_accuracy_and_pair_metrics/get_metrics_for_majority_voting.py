import json
import os

from tabulate import tabulate


def get_result_gpt(response:str):
    index=response.lower().find("decision")
    re=response[index:].lower()
    if re.find("yes")!=-1:
        return 1
    elif re.find("no")!=-1:
        return 0
    else:return -1
def get_metrics_majority_voting(data_file):
    contain_result=[]
    pair_result = {}

    if not os.path.exists(data_file):
        return (0, 0)

    with open(data_file, 'r', encoding="utf-8") as f:
        if data_file.endswith(".jsonl"):
            datas = f.readlines()
        else:
            datas=json.load(f)
        table_data = []
        table_index = 1

        for index in range(16):
            count=0
            contain=[0,0]
            accuracy = {
                'before': [0, 0],
                'after': [0, 0],
                'non': [0, 0],
            }
            for d in datas:

                contain[1]+=1
                if data_file.endswith(".jsonl"):
                    d = json.loads(d)
                accuracy[d["type"]][1] += 1
                preds = [get_result_gpt(i) for i in d["respond"]][:index + 1]
                preds = [i  for i in preds]
                number_of_one = preds.count(1)
                number_of_zero = preds.count(0)
                if d["target"] ==1 and number_of_one!=0:
                    contain[0]+=1
                if d["target"] ==0 and number_of_zero!=0:
                    contain[0]+=1
                if number_of_one==number_of_zero:
                    count+=1
                p = 1 if number_of_one >= number_of_zero else 0
                p = p if p != -1 else 0
                if p == d["target"]:
                    accuracy[d["type"]][0] += 1
                if d["type"] != "non":
                    if d["pair_index"] not in pair_result.keys():
                        pair_result[d["pair_index"]] = {"before": -1, "after": -1}
                    pair_result[d["pair_index"]][d["type"]] = p

            accuracy_data = {}
            for key in accuracy.keys():
                acc = accuracy[key][0] / accuracy[key][1] if accuracy[key][1] > 0 else 0
                accuracy_data[key] = f"{acc:.4f}"
            before = accuracy["before"][0] / accuracy["before"][1]
            after = accuracy["after"][0] / accuracy["after"][1]
            non = accuracy["non"][0] / accuracy["non"][1]
            bm1 = 3 * 3 / (1 / ((1 / 3) * before) + 1 / ((1 / 3) * after) + 1 / ((1 / 3) * non))
            pair_metric = [0, 0, 0, 0]
            for key, value in pair_result.items():
                assert value["before"] != -1 and value["after"] != -1
                index = value["before"] * 2 + value["after"]
                pair_metric[index] += 1

            total_pair = sum(pair_metric)
            pair_metric = [i / total_pair if total_pair > 0 else 0 for i in pair_metric]
            contain_result.append(contain[0]/contain[1])
            row = [table_index] +[contain[0]/contain[1]]+ list(accuracy_data.values()) +[bm1]+ [
                f"{pair_metric[2]:.4f}", f"{pair_metric[3]:.4f}", f"{pair_metric[0]:.4f}", f"{pair_metric[1]:.4f}"
            ]
            table_data.append(row)

            table_index += 1

        headers = [
            "Number", "Contain","Accuracy before", "Accuracy after", "Accuracy non","BM1",
            "P-C", "P-V", "P-B", "P-R"
        ]

        print(tabulate(table_data, headers=headers, tablefmt="plain", floatfmt=".4f"))
        return contain_result
if __name__ == "__main__":
    get_metrics_majority_voting("results/our_test_qwen-2.5-coder-for-majority-voting.jsonl")