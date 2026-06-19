# ClinVar Variant Pathogenicity Classifier

A machine learning-based system to classify **missense single nucleotide variants (SNVs)** as pathogenic or benign, built as a full-stack web application with a Flask backend and an interactive frontend for VCF-based predictions.

---

## Scope of the Study

This project develops an AI model to classify genetic variants based on their disease impact, supporting precision medicine and clinical variant interpretation.

- **Focus:** Missense SNVs — variants that cause a single amino acid change in a protein
- **Data source:** ClinVar database (clinically curated variant information)
- **Classification:** Variants are categorized into four classes — **Benign, Likely Benign, Pathogenic, Likely Pathogenic**
- **Preprocessing:** Duplicate removal and filtering of variants with incomplete information
- **Features extracted:** Allele frequency, amino acid substitution, evolutionary conservation, and functional prediction scores (PolyPhen, SIFT, CADD, PhyloP, PhastCons)
- **Models trained:** Logistic Regression, Random Forest, XGBoost
- **Evaluation metrics:** Accuracy, Precision, Recall, F1-score
- **Goal:** Assist researchers and clinicians in interpreting genetic variants

**Note:** The scope is limited to computational prediction on missense SNVs, without experimental validation.

---

## Tech Stack

| Layer | Tools |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| ML Models | Logistic Regression, Random Forest, XGBoost, SVM |
| Dev Tools | Jupyter Notebook, VS Code |

---

## How It Works

1. User pastes or uploads a `.vcf` file through the web interface
2. Flask backend parses the VCF using `backend_utils.py`
3. Features extracted per variant (positional, allele frequency, PolyPhen, SIFT, CADD, PhyloP, review status, gene info, quality scores)
4. Trained ML model predicts variant classification
5. Confidence score returned per variant

---

## Features Used (34 total)

- **Positional:** CHROM, POS, REF/ALT encoding, SNP/INDEL flags
- **Population frequency:** AF_ESP, AF_EXAC, AF_TGP
- **Functional prediction:** PolyPhen score/category, SIFT score/category
- **Conservation:** CADD, PhyloP, PhastCons
- **Clinical annotation:** Review status, homozygous flags, RS ID
- **Variant quality:** DP, MQ, FS, SOR, QD

---

## Run Locally

```bash
git clone https://github.com/Nivasini2327/clinvar-variant-classifier.git
cd clinvar-variant-classifier
pip install -r requirements.txt
python app.py
```
Then open `http://localhost:5000` in your browser.

---

## Dataset

Due to GitHub file size limits, the full ClinVar VCF file is not included in this repository.

Download the full dataset directly from NCBI:
🔗 https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz

Place the downloaded file in the `data/` folder to reproduce the pipeline.

---

## Project Structure

```
├── app.py                       → Flask API with /predict endpoint
├── backend_utils.py             → VCF parser + feature extractor
├── requirements.txt
├── templates/
│   └── index.html               → Web interface
├── static/
│   ├── styles.css
│   └── script.js
├── models/
│   └── best_model.pkl           → Saved trained model
├── data/
│   ├── X_train.npy / X_test.npy / X_val.npy
│   └── y_train.npy / y_test.npy / y_val.npy
├── notebooks/
│   ├── model_training.ipynb
│   └── backend_development.ipynb
├── config/
│   ├── categorical_mappings.json
│   └── feature_names.json
└── results/
    ├── test_predictions.csv
    └── report.html


[LinkedIn](https://www.linkedin.com/in/shrreya-nivasini-d-396970308/)
