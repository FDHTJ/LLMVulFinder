# LLMVulFinder: Letting Large Language Models Tell All

This paper presents LLMVulFinder, a methodology that enables small LLMs (parameter size < 10B) to effectively identify vulnerable code while providing root-cause explanations.
Our main contribution are as follows:

### 1.Provide a Clean Dataset for Vulnerability Detection

We carefully selected code snippets that genuinely reflect vulnerabilities from the BigVul and MegaVul datasets to create a clean root cause dataset. For more details on our data cleaning process, please refer to [Data Cleaning](data_preparation/data_clean/README.md). Additionally, we performed the `train/train_only_pairs` experiment to validate that using root cause pairs improves model performance. Our results show that the model 
trained on our pairs performs better on PrimeVul test pairs than on PrimeVul train pairs.

### 2.Provide Clear Explanation for Each Code

We further leverage the capabilities of large language models, along with existing CVE and CWE descriptions, to generate high-quality explanations for each vulnerability. For patched and safe code, we only retain it if the language model confirms that it is indeed not vulnerable. This process ensures that we obtain high-quality, corresponding explanations for each code snippet, which can then be used to train a smaller model. For more details, see [Data Distillation](data_preparation/data_distillation).
And our final dataset can be found in ```data_preparation/final_data```, and the brief introduction is in [Data Preparation](data_preparation/README.md).

### 3.Train Smaller model


We use our dataset to train a smaller model (with parameter size < 10B), and its performance outperforms strong baselines. Additionally, our trained model provides better responses with fewer tokens, reducing cost. For details on training the language model , refer to [Language Model](train/language_model/README.md). The evaluation process can be found in the `evaluation` folder.  
For the training and evaluation of LineVul and SVulD, please refer to the `train/pretrained_model` folder.

### 4.RVBS

We further enhance model performance by scaling test time. In practice, we use Random-Forest Verifier Best-of-N Search to select the best answer. For more details on training RVBS, refer to the [RVBS](train/RVBS/README.md). The evaluation of RVBS can be found in evaluation/compute_accuracy_and_pair_metrics/get_metrics_for_RVBS.py.

### 5. Balanced Metric

Many methods currently evaluate performance using the F1-score; however, their test sets are often highly imbalanced, with safe code making up the majority. This imbalance can significantly affect the F1-score. For example, consider a model that predicts both vulnerable and safe code with 90% accuracy. If there are 100 test examples of each, the true positives (TP) would be 90, false positives (FP) 10, true negatives (TN) 90, and false negatives (FN) 10. This gives a precision of 0.9 (TP / (TP + FP)), recall of 0.9, and an F1-score of 0.9.

However, if the test set consists of 100 vulnerable code examples and 1,000 safe code examples (a more common scenario in some datasets), the TP remains 90, but FP increases to 100, while TN is 900 and FN is still 10. This results in a precision of 0.4737, recall of 0.9, and an F1-score of 0.6207. Clearly, F1-score can be misleading in such imbalanced datasets.

Even in our case, where the data is only slightly imbalanced (vulnerable vs. non-vulnerable=1:2), we are concerned that the F1-score may fail to capture the model’s actual ability in vulnerability detection. For example, suppose the test set contains 100 vulnerable and 100 non-vulnerable samples. Consider two models:
Model 1: 50% accuracy on patched code, 60% accuracy on regular code, and 50% accuracy on vulnerable code.
Model 2: 30% accuracy on patched code, 80% accuracy on regular code, and 50% accuracy on vulnerable code.


When computing the F1-score:
For Model 1: Recall = 0.5, Precision = 50 / (50 + 100 × 0.5 + 100 × 0.4) = 0.357
For Model 2: Recall = 0.5, Precision = 50 / (50 + 100 × 0.7 + 100 × 0.2) = 0.357
Both models thus achieve the same recall, precision, and F1-score. However, we argue that Model 1 is more powerful because it better distinguishes complex non-vulnerable code (i.e., patched code).


When evaluating with the balanced metric (BM):
Model 1: BM = 3 / (1/0.5 + 1/0.5 + 1/0.6) = 0.529
Model 2: BM = 3 / (1/0.5 + 1/0.3 + 1/0.8) = 0.456
We contend that Model 1 is more valuable, since distinguishing vulnerable from patched code is more indicative of true vulnerability understanding. Nonetheless, we appreciate the suggestion. For completeness, and to facilitate comparison with a broader body of related work, we will include the F1-score in the final version of our paper—alongside our primary metrics and this discussion of its limitations.


To address this issue, it is important to evaluate the model's performance in a way that is not heavily influenced by the ratio of positive to negative samples. Our analysis shows that, even when the test set changes, the accuracy for both vulnerable and safe code remains stable. We also identified three distinct categories of code: vulnerable, patched, and ordinary. Therefore, we propose using the accuracy across all three types of code, and calculating the harmonic mean of these accuracies as a balanced and stable metric to assess the model's vulnerability detection capability.


