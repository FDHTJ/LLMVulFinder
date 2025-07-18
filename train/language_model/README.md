## Setup

1. **Create a Conda Environment**
   
   Use the following command to create and activate a new environment for the SFT training:
   
   ```bash
   conda create -n sft_env python=3.9
   conda activate sft_env
   ```
2. **Install Dependencies**
   
   After activating the environment, install all required dependencies by running:
   
   ```bash
   pip install -r requirements.txt
   ```
3. **Binarize Data**
   
   Take training Qwen-2.5-coder as an example:
   Assuming that you have merged the training dataset into ```train_data_for_qwen_coder.json```
   You can run the ``` get_train_for_qwen_coder("train_data_for_qwen_coder.json")```,and you will get a jsonl file named ```train_data_for_qwen_coder.jsonl```, in which each line is a json object formed like:
   ```json
   {
        "messages":[
            {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
            {"role": "user", "content": "......"},
            {"role": "assistant", "content": "......"}
       ],
       "format": "chatml"
   }
   ```
   Then run as below to binarize the raw data:
   
   ```bash
   python binarize_data_for_qwen_coder.py \
   --input_path train_data_for_qwen_coder.jsonl\
   --output_path processed_train_data_for_qwen_coder.jsonl
   ```
4. **Training**
   Once the environment is ready and the model paths are configured, run the evaluation suite by executing the following script:
   
   ```bash
   python train_for_qwen_coder.py\
   --data_path processed_train_data_for_qwen_coder.jsonl\
   --model_name_or_path your_model_path\
   --output_dir your_output_path
   ```


