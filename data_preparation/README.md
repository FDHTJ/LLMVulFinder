### Data Preparation

Our data preparation process consists of two main components:

1. **Data Cleaning**  
   We remove erroneous or low-quality cases identified in the original dataset to ensure a cleaner and more reliable training corpus.

2. **Data Distillation**  
   We perform knowledge distillation to generate high-quality training samples for fine-tuning a smaller model.  
   Since data selection is also involved in this step, the distillation process can be regarded as a more advanced form of data cleaning.

### Original Datasets

The original datasets used in this project are:

- **Big-Vul**: [MSR 20 Code Vulnerability Dataset](https://github.com/ZeoVan/MSR_20_Code_Vulnerability_CSV_Dataset)  
- **Mega-Vul**: [MegaVul](https://github.com/Icyrockton/MegaVul)

