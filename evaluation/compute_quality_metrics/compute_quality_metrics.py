import json
import bleu
from rouge_score import rouge_scorer
from bert_score import score
def calculate_bertscore(preds, refs):
    print("BertScore")
    for pred in ["o4_mini", "gpt_4o", "qwen_trained", "seed_coder_trained", "star_coder_trained"]:
        if pred not in preds.keys() :
            continue
        print("=" * 30)
        print(pred)

        for ref in ["cve_description", "ground_truth", "commit_log", "cwe_description"]:
            if pred not in preds.keys() or ref not in refs.keys():
                continue
            P, R, F1 = score(preds[pred], refs[ref], lang="en")
            avg_f1 = sum(F1) / len(F1)
            print(f"BERTScore F1 {ref}:", avg_f1.item())
def calculate_rouge(preds, refs):
    print("Rouge")
    rouge = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    for pred in ["o4_mini", "gpt_4o", "qwen_trained", "seed_coder_trained", "star_coder_trained"]:
        if pred not in preds.keys() :
            continue
        print("=" * 30)

        print(pred)
        for ref in ["cve_description", "ground_truth", "commit_log", "cwe_description"]:
            if pred not in preds.keys() or ref not in refs.keys():
                continue
            rouge_scores = [rouge.score(ref_text, pred_text) for ref_text, pred_text in zip(refs[ref], preds[pred])]
            avg_rouge = {key: sum([score[key].fmeasure for score in rouge_scores]) / len(rouge_scores) for key in
                         rouge_scores[0].keys()}
            print(f"ROUGE {ref}:", avg_rouge)
def calculate_blue(preds, refs):
    print("BLUE")
    for pred in ["o4_mini","gpt_4o","qwen_trained","seed_coder_trained","star_coder_trained"]:
        if pred not in preds.keys() :
            continue
        print("="*30)

        print(pred)
        for ref in ["cve_description", "ground_truth","commit_log" ,"cwe_description"]:
            if pred not in preds.keys() or ref not in refs.keys():
                continue
            (goldMap, predictionMap) = bleu.computeMaps(preds[pred], refs[ref])
            bleu_score = round(bleu.bleuFromMaps(goldMap, predictionMap)[0], 2)
            print(f"{ref}:",bleu_score)
is_gpt=False
with open("our_vulnerable_code_with_more_information.json","r",encoding="utf-8") as f:
    data=json.load(f)
    print(len(data))
    preds={}
    refs={}
    for d in data:
        for pred in ["o4_mini","gpt_4o","qwen_trained","seed_coder_trained","star_coder_trained"]:
            if pred not in preds.keys():
                preds[pred]=[]
            preds[pred].append(d[pred])
        for ref in ["cve_description","ground_truth","commit_log","cwe_description"]:
            if ref not in refs.keys():
                refs[ref] = []
            refs[ref].append(d[ref])
calculate_blue(preds,refs)
calculate_rouge(preds,refs)
calculate_bertscore(preds, refs)
