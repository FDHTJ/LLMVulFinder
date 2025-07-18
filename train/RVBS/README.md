- **Get Data for Reward Model Training** 
    Assuming that you have merged the training dataset into ```train_data_for_qwen_coder.json```, then you can get training data for reward model by running:
    ```bash
    python get_train_data_for_reward_model.py\
    --model_path your_model_path\
    --data_path train_data_for_qwen_coder.json
    ```
--