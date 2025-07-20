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

