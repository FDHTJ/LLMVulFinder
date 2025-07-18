## Data Cleaning

### 1. Removing Functions Without Bodies

In the Big-Vul or Mega-Vul dataset, some functions have no function bodies. Since our focus is on **function-level vulnerability detection**, we discard samples in the following cases:

- The **original function** (before modification) is only a declaration or has an empty body.
- The entire function is **deleted** during the commit (i.e., only the declaration remains).
- The **modified function** (after modification) becomes a declaration (e.g., the file turns into a header file).

We define the following rule to determine whether a function is valid:

> If a function contains both a **left brace `{`** and a **right brace `}`**, and the content between them is **non-empty** (excluding only `\n`, `\t`, or spaces), we consider it a valid, complete function.

Only if **both** the `func_before` and `func_after` satisfy this rule will the sample be retained.

---

### 2. Removing Samples with Multiple Functions

Some `func_before` or `func_after` fields in original dataset may contain **multiple functions**, but we focus on single-function vulnerability detection to maintain consistency.

To filter such cases, we utilize [**Joern**](https://github.com/joernio/joern) to analyze the number of functions:

- We save each `func_before` and `func_after` as `.c` or `.cpp` files.
- We then use Joern to generate **Code Property Graphs (CPGs)** for each file.
- By analyzing the CPGs, we determine the number of functions in the file.
- If a sample contains multiple functions, it is **discarded** to ensure clarity and precision.

---

**The code about procedure 1 and 2 can be found in ```joern.py```.**

### 3. Removing Inaccurate Labels

In original dataset, a function is labeled as "vulnerable" if it was modified in a vulnerability-related commit. However, through analysis, we found that this labeling strategy is often **inaccurate**.

What we aim to identify is the **code snippet that best reflects the CVE (Common Vulnerabilities and Exposures) description**. To improve label quality, we employ large language models (LLMs), specifically **GPT-4o-mini** and **GPT-o4-mini**, to filter the data using the following prompt:


#### (1) Prompt for Data Filtering

We use the following prompt format to guide large language models (LLMs) in identifying whether a code snippet contains the vulnerability described in a CVE:

---
**Code:**

insert code here

**CVE Description:**

insert cve description here

**Instruction:**

The vulnerability of code refers to weaknesses or flaws that can be exploited by attackers to compromise the security of a system. Each code with vulnerability usually has a corresponding CVE (**Common Vulnerabilities and Exposures**) description. Each CVE provides a standardized way to identify, describe, and catalog publicly disclosed security vulnerabilities and exposures. A CVE entry contains a unique identifier for a specific vulnerability, along with a description that outlines the nature of the issue, its impact, and other relevant details.

Based on the code and CVE description provided, analyze whether the code contains the vulnerability described in the CVE. 
If the provided code includes a fix for the vulnerability described in the CVE, it should be considered **non-vulnerable**.

Please think step by step and provide your answer in the following format:



**Analysis**:

[Analyze the relationship between CVE and code step by step]

**Decision**:

[Yes (vulnerable) / No (non-vulnerable) based on the above analysis]

---
#### (2) Filtering Pipeline

we think that if the model can detect the vulnerability in vulnerable code and figure out the fixed solution in patched code,
then the code indeed reflects the vulnerability described in CVE.

- For all `func_before` and `func_after` pairs, we first query **GPT-4o-mini** using the above prompt.
    - If `func_before` is judged **vulnerable** and `func_after` **non-vulnerable**, the sample is **kept**.
- Samples discarded by GPT-4o-mini are then passed to **GPT-o4-mini** for a second round of evaluation using the same prompt.
    - If GPT-o4-mini meets the same criteria, we **retain** those additional high-quality samples.

---


