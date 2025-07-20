## Get Response from Trained Model and GPT
- **Get Respond From trained model**
    Here we provide the code that we get the response from the trained model ```eval_{model}_trained_model_batch.py```,
    You can run the code like:
    ```bash
    python eval_qwen_coder_trained_model_batch.py\
    --model_path "your trained model"\
    --data_path "your data"
    ```
- **Get Respond From OpenAI**
    
    To get the response from the GPT-4o and GPT-o4-mini, you can run code like:
    ```bash
    python eval_GPT.py\
    --model "the model you want to use"\
    --file "your data file"
    ```

## Compute Metrics

- **Compute Accuracy and Pair Metrics**
    
    All the result of response from GPT model and our trained model can be found in ```compute_accuracy_and_pair_metrics/results```,
    And the code to compute the metrics (include majority voting and RVBS) can also be found in ```compute_accuracy_and_pair_metrics```,
    For majority voting and RVBS, you can simply run the code ```get_metrics_for_majority_voting.py``` and ```get_metrics_for_RVBS.py```.
    For the response from our trained model and GPT model, you can run like:
    ```bash
    python get_metrics.py\
    --model "qwen-2.5-coder-trained"\
    --type "our"
    ```
    You can check the files under the folder to see all the value of "model".
- **Compute Generated Quality Metrics**
  
  Despite the accuracy and pair metrics, we also leverage BLEU-4, RougeL, and Bert-Score to evaluate the generation quality.
  We calculate these metrics on distilled information, CVE description, CWE description, and commit logs.
  You can run the code ```compute_quality_metrics/compute_quality_metrics.py``` or find the result in RQ-2 in our paper to see the performance.
  
  Besides, we claim that our trained model can generate more human-like explanation. And we verify this by compute the metrics between response from different model and the human vulnerability explanation in [TopScoreWrongExam](https://github.com/niklasrisse/TopScoreWrongExam/tree/main).
  You can also find the result in ```compute_quality_metrics/response_for_39_examples_in_top_score_wrong_exam.json``` and calculate metrics by running ```compute_quality_metrics/compute_quality_metrics_for_top_score_wrong_exam.py```.

  **Tips: Before runing the code, the model named roberta-large is expected to be downloaded into the folder ```roberta-large``` or make sure you can access [HuggingFace](https://huggingface.co/).**