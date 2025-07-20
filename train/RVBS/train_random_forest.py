import argparse
import ast
import json
import re
from itertools import accumulate

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from joblib import load

# feature_cols = ['rel_max', 'rel_mean', 'rel_mean', 'rel_size', 'rel_accumu']
# feature_cols = ['max', 'min', 'mean', 'std', 'size', 'accumu']
feature_cols = ['accumu']


def read_file(path):
    with open(path, 'r') as f:
        return [json.loads(line) for line in f]

parser = argparse.ArgumentParser()
parser.add_argument("--train_data_path",
                    default='train_for_random_forest_balanced_with_16_answers.jsonl',
                    type=str,
                    help="path of input data")
parser.add_argument("--eval_data_path",
                    default='train_for_random_forest_balanced_with_16_answers.jsonl',
                    type=str,
                    help="path of input data")
parser.add_argument("--model_path",
                    default='random_forest.joblib',
                    type=str,
                    help="path to save processed data")
args = parser.parse_args()


def get_result(response: str) -> int:
    """
    Extrat decision from the answer：
      - "yes" → 1
      - "no"  → 0
      - else  → -1 # no conclusion
    """
    response = response.lower()
    idx = response.find("decision")
    snippet = response[idx:].lower() if idx != -1 else response
    if "yes" in snippet:
        return 1
    elif "no" in snippet:
        return 0
    else:
        return -1

def check(answer, next_line_gt, subsequent_values_gt):
    if answer == None:
        return False
    current_line, program_state, next_line = answer

    if [current_line, program_state] == subsequent_values_gt[0] and next_line == next_line_gt:
        return True
    else:
        return False


def group_size(bits: list[int]) -> dict[int, list[int]]:

    result = {0: [], 1: []}
    for idx, bit in enumerate(bits):
        if bit in result:
            result[bit].append(idx)
        else:
            continue
    return {k: v for k, v in result.items() if v}


def generate_sample_data():
    data = []
    with open(args.train_data_path,'r')as r:
        lines = r.readlines()
        for i,l in enumerate(lines):
            item=json.loads(l)
            answers = item['respond']
            scores = item['rewards']
            extracted = [get_result(answer) for answer in answers]
            freq = group_size(extracted)
            for k in freq.keys():
                group_scores = []
                for va in freq[k]:
                    group_scores.append(scores[va])
                max_val = np.max(group_scores)
                min_val = np.min(group_scores)
                mean_val = np.mean(group_scores)
                std_val = np.std(group_scores)
                size_val = np.size(group_scores)
                accumulate_val = np.sum(group_scores)
                result = get_result(answers[freq[k][0]])
                if result==item['target']:
                    label = 1
                else:
                    label = 0
                data.append([i, k, max_val, min_val, mean_val, std_val, size_val, accumulate_val, label])
    return pd.DataFrame(data, columns=['sample_id', 'group_id', 'max', 'min', 'mean','std', 'size', 'accumu', 'label'])

def predict_best_group(new_sample_df, model):
    new_sample_df = compute_relative_features(new_sample_df)
    features = new_sample_df[feature_cols]

    probas = model.predict_proba(features)
    scores = probas[:, 1]

    new_sample_df['score'] = scores
    best_group = new_sample_df.loc[new_sample_df['score'].idxmax()]
    return best_group['result'], new_sample_df


# calculate features
def compute_relative_features(df):
    # calculate gloable features for every sample
    grouped = df.groupby('sample_id')
    global_stats = grouped[['max', 'min', 'mean', 'size','accumu']].agg({
        'max': ['max', 'min'],
        'min': ['max', 'min'],
        'mean': ['max', 'min'],
        'accumu': ['max', 'min'],
        'size': ['max', 'min']
    })

    global_stats.columns = ['global_max_max', 'global_max_min',
                            'global_min_max', 'global_min_min',
                            'global_mean_max', 'global_mean_min',
                            'global_accumu_max', 'global_accumu_min',
                            'global_size_max', 'global_size_min']
    df = df.merge(global_stats, on='sample_id', how='left')

    # calculate relative feature
    df['rel_max'] = (df['max']) / (df['global_max_min'] )
    df['rel_min'] = (df['min'] ) / (df['global_min_min'])
    df['rel_mean'] = (df['mean']) / (df['global_mean_min'])
    df['rel_size'] = df['size'] / df['global_size_min']
    df['rel_accumu'] = df['accumu'] / df['global_accumu_min']


    df['inv_std'] = 1 / (df['std'] + 1e-6)


    df['rel_min_sq'] = df['rel_min'] ** 2

    return df


df = generate_sample_data()
df = compute_relative_features(df)


X = df[feature_cols]
y = df['label']

# train random forest
model = RandomForestClassifier(
    n_estimators=225,
    max_depth=4,
    random_state=42,
    class_weight='balanced'
)
model.fit(X, y)

# evaluate
y_pred = model.predict(X)
print("\nClassification Report:")
print(classification_report(y, y_pred))

from joblib import dump
dump(model, args.model_path)

data=read_file(args.eavl_data_path)

# rf_model = load('random_forest.joblib')


num_true=0


with open('result_of_rvbs.jsonl','w')as w:
    sum = len(data)
    for i, item in enumerate(data):
        data = []
        answers = item['respond']
        scores = item['rewards']
        extracted = [get_result(answer) for answer in answers]
        freq = group_size(extracted)
        for k in freq.keys():
            group_scores = []
            for va in freq[k]:
                group_scores.append(scores[va])
            max_val = np.max(group_scores)
            min_val = np.min(group_scores)
            mean_val = np.mean(group_scores)
            std_val = np.std(group_scores)
            size_val = np.size(group_scores)
            accumulate_val = np.sum(group_scores)
            result = get_result(answers[freq[k][0]])

            data.append([i, result, max_val, min_val, mean_val, std_val, accumulate_val, size_val])
        sample = pd.DataFrame(data, columns=['sample_id', 'result', 'max', 'min', 'mean', 'std', 'accumu', 'size'])
        final_result, sample_new = predict_best_group(sample, model)
        item['final_result']=int(final_result)
        if int(final_result)==item['target']:
            num_true += 1
        w.write(json.dumps(item)+'\n')
print(num_true)
print(sum)
print(num_true / sum)

