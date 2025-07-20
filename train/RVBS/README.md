- **Get Data for Reward Model Training** 
    
    Assuming that you have merged the training dataset into ```train_data_for_qwen_coder.json```, then you can get training data for reward model by running:
    ```bash
    python get_train_data_for_reward_model.py\
    --model_path your_model_path\
    --data_path train_data_for_qwen_coder.json
    ```
- **Get Train Pairs for Reward model**

    Then you can run the ```get_train_pairs_for_reward_model.py``` to get the pairs.

- **Training Reward Model**
    
    When the data get ready, please train the reward model by:
    ```bash
    python train_reward_model.py\
    --model_name your_model_path\
    --train_set_path train_data_for_qwen_coder_pairs_for_reward_model.jsonl
    ```
- **Generate Data for Random Forest**
    
    Before you train the random forest, you need to get the scores for each answer for the training dataset by:
    ```bash
    python inference_of_reward_model.py\
    --model_path your_trained_reward_model\
    --data_path train_data_for_qwen_coder_for_reward_model.jsonl
    ```
- **Train and Evaluate Random Forest**

  Finally, you can train and evaluate the random forest by:
  ```bash
  python train_random_forest.py\
  --train_data_path "the result of Generate Data for Random Forest"\
  --eval_data_path "the data you want to evaluate by random forest"
  ```
  The evaluate data is expected to contain the same number of answers from trained model and scores from reward model.
  And the result will be saved into ```result_of_rvbs.jsonl```, then you can go to ```evaluation/README.md``` to get the metrics of the data.