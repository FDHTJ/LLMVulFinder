# LLMVulFinder: Letting Large Language Models Tell All

This paper presents LLMVulFinder, a methodology that enables small LLMs (parameter size < 10B) to effectively identify vulnerable code while providing root-cause explanations
Our main contribution are as follows:

### 1.Provide a Clean Dataset for Vulnerability Detection

We carefully selected code snippets that genuinely reflect vulnerabilities from the BigVul and MegaVul datasets to create a clean root cause dataset. For more details on our data cleaning process, please refer to [Data Cleaning](data_preparation/data_clean/README.md). Additionally, we performed the `train/train_only_pairs` experiment to validate that using root cause pairs improves model performance. Our results show that the model 
trained on our pairs performs better on PrimeVul test pairs than on PrimeVul train pairs.

### 2.Provide Clear Explanation for Each Code

We further leverage the capabilities of large language models, along with existing CVE and CWE descriptions, to generate high-quality explanations for each vulnerability. For patched and safe code, we only retain it if the language model confirms that it is indeed not vulnerable. This process ensures that we obtain high-quality, corresponding explanations for each code snippet, which can then be used to train a smaller model. For more details, see [Data Distillation](data_preparation/data_distillation).
And our final dataset can be found in ```data_preparation/final_data```, and the brief introduction is in [Data Preparation](data_preparation/README.md).

### 3.Train Smaller model

We use our dataset to train the smaller model(parameter size < 10B), and its performance is better than strong baselines. And our trained model can give a better response with less token cost. See the train for language models and RVBS at [Language model](train/language_model/README.md) and [RVBS](train/RVBS/README.md) and the evaluation process is in the folder ```evaluation```.
For the training and evaluation of LineVul and SVulD, you can turn to the folder ```train/pretrained_model```.