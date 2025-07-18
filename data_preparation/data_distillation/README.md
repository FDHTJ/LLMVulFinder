#  Data Distillation

In the data cleaning stage, we only process samples labeled as vulnerable. After gathering all vulnerable samples, we randomly sample an equal number of non-vulnerable samples from the original dataset (where `func_before` is identical to `func_after`) to construct the final dataset.

We then apply **data distillation** using GPT-4O on both the vulnerable and non-vulnerable samples. The prompts used for each category are shown below.

---

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

