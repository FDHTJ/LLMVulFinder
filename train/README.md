### 🔧 Model Training

- **Large Language Models**:  
  We utilize the official implementation from [Qwen2.5-Coder](https://github.com/QwenLM/Qwen2.5-Coder/tree/main) to fine-tune several large language models, including:
  - [Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct)
  - [StarCoder2-7B](https://huggingface.co/bigcode/starcoder2-7b)
  - [SeedCoder-8B-Instruct](https://huggingface.co/ByteDance-Seed/Seed-Coder-8B-Instruct)



- **Pretrained Code Models**:  
  For lightweight pretrained models such as `LineVul` and `SVulD`, we adopt the implementation provided in [SVulD repository](https://github.com/jacknichao/SVulD).


- **Training with Only Pairs**:

  We further conduct experiments using only the paired samples from our dataset and those from [PrimeVul](https://github.com/DLVulDet/PrimeVul) to train pretrained models.  
  Evaluation is performed on both our dataset's pairs and PrimeVul's pairs.  
  The results demonstrate that our root-cause-based pairs help the model learn more effectively and generalize better.
