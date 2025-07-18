#  Data Distillation

In the data cleaning stage, we only process samples labeled as vulnerable. After gathering all vulnerable samples, we randomly sample an equal number of non-vulnerable samples from the original dataset (where `func_before` is identical to `func_after`) to construct the final dataset.

We then apply **data distillation** using GPT-4O on both the vulnerable and non-vulnerable samples. The strategy and prompts used for each category are shown below.

---
## Distillation Strategy and Rationale

### Input Structure

For **vulnerable** samples, we provide the model with:

- The full code snippet  
- CVE description  
- CWE (Common Weakness Enumeration) description  
- The vulnerable lines (i.e., lines deleted or modified in `func_after`)  

For **non-vulnerable** samples, we only provide the code and ask the model to assess its vulnerability without any external context.

---

### Functional First

Each prompt is designed to have the model **perform a neutral functional analysis first**, before making any security judgment.  
This ensures better contextual understanding and leads to more accurate vulnerability detection.

---

### Filtering Based on Model Judgment

We do **not** force the model to conform to original labels. Instead, we leverage the model's own decision to refine the dataset:

- If a **vulnerable-labeled** sample is judged by the model as **non-vulnerable** (even with full context), it is discarded — indicating the vulnerability is unclear or possibly mislabeled.
- If a **non-vulnerable-labeled** sample is judged by the model as **vulnerable** (despite lacking context), it is also discarded — reflecting possible ambiguity or spurious patterns.

In earlier filtering stages, we ensured that both `func_before` and `func_after` are closely aligned with the root cause described in the CVE.  
To reinforce this during distillation, we also include `func_after` as a **negative example**.

If the model mistakenly judges a `func_after` as vulnerable, we discard the corresponding `func_before` as well — since its contrastive value becomes invalid.

---

### Distillation Goal

Our goal is to **distill core vulnerability knowledge**, rather than training a model to rely on context clues or dataset-specific patterns.  
This approach ensures that smaller downstream models can **learn to detect vulnerabilities based on code behavior**, not superficial correlations.


## Distillation Prompt for Vulnerable Code


**Code:**

*(Insert code here)*

**CVE Description:**

*(Insert CVE text here)*

**CWE Description:**

*(Insert CWE text here)*

**Vulnerable Lines:**

*(Insert line numbers or excerpts here)*

---

### Instructions:

You are given a code snippet, a CVE description, a CWE description, and potentially vulnerable lines. Your task is to **analyze the code with the provided information**, and identify whether the given code contains vulnerability or not.

Please respond in the following format:

1. **Functional Analysis**
    
    Neutrally describe what each part of the code is intended to do. Do not mention any issues or potential vulnerabilities.
    
2. **Vulnerability Analysis**
    
    Based on the code, the **functional analysis**, the given CVE and CWE, and the potentially vulnerable lines, assess whether the code contains vulnerability or not.
    
    - Don’t assume a flaw or that the code is safe—verify and assess logically.
    - **Do not** reference CVE/CWE identifiers or domain‑specific terminology.
    
3. **Decision**
    
    **Yes/No.** [A brief summary of your conclusion.]


## Distillation Prompt for Non-Vulnerable
**Code:**

*(Insert code here)*

---

### Instructions:

You are given a code snippet that is likely not vulnerable. Your task is to analyze the code and determine if it contains any vulnerabilities. 

Please respond in the following format:

1. **Functional Analysis**
    
    Neutrally describe what each part of the code is intended to do. Do not mention any issues or potential vulnerabilities.
    
2. **Vulnerability Analysis**
    
    Based on the code’s behavior, explain what vulnerabilities the code is susceptible to, whether the code prevents these vulnerabilities from occurring, or whether the code actually contains these vulnerabilities. 
    
    - Don’t assume a flaw or that the code is safe—verify and assess logically.
    
3. **Decision**

    Yes/No. [A brief summary of your conclusion.]

