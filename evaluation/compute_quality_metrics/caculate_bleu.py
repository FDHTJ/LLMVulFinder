import json
import bleu
golds=[]
summaries=[]
path='/home/dell/dl/LLMEvaluation/results/code2nl/deepseek_distill_qwen_7b.jsonl'
with open(path,'r')as r:
    lines=r.readlines()
    for l in lines:
        item=json.loads(l)
        if 'slimcode' in path:
            gold=item['nl']
        else:
            gold=' '.join(item['docstring_tokens'])
        try:
            summary=item['model_output'].split('[SUMMARY]')[1].split('[/SUMMARY]')[0].strip()
            # print(summary)
            summaries.append(summary)
            golds.append(gold)
            # print(item['model_output'])
        except:
            print('*****************')
            print(item['model_output'])
# caculate bleu
# golds = open(os.path.join(args.output_dir, "test_gold"), 'r')
# summaries=open(os.path.join(args.output_dir, "test_output_summary"), 'r')
(goldMap, predictionMap) = bleu.computeMaps(summaries, golds)
bleu_score = round(bleu.bleuFromMaps(goldMap, predictionMap)[0], 2)
print(bleu_score)