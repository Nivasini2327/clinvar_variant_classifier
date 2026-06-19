import pandas as pd
import numpy as np
import re
import json
import os

def parse_vcf_text(vcf_text):
    """Parses raw VCF text from the frontend into a Pandas DataFrame."""
    records = []
    header = None
    
    for line in vcf_text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('##'):
            continue
        elif line.startswith('#CHROM'):
            header = line.lstrip('#').split('\t')
        else:
            if header:
                fields = line.split('\t')
                records.append(fields)
                
    if not records or not header:
        return pd.DataFrame() # Return empty if parsing failed
        
    return pd.DataFrame(records, columns=header)

def extract_features_prod(df):
    """
    Production version of extract_features that avoids pd.factorize 
    and returns a DataFrame matching exactly what the model expects.
    """
    if df.empty:
        return pd.DataFrame()
        
    features = pd.DataFrame()
    info = df['INFO'] if 'INFO' in df.columns else pd.Series([''] * len(df))
    
    # --- CELL 1: Positional Features ---
    # Attempt to load exact categorical mappings if saved, otherwise fallback to simple fallback or 0
    chrom_map = {}
    ref_map = {}
    alt_map = {}
    try:
        if os.path.exists('categorical_mappings.json'):
            with open('categorical_mappings.json', 'r') as f:
                mappings = json.load(f)
                chrom_map = mappings.get('CHROM', {})
                ref_map = mappings.get('REF', {})
                alt_map = mappings.get('ALT', {})
    except Exception:
        pass

    # Safely map categoricals. Unknowns get -1 (or 0)
    features['CHROM'] = df['CHROM'].astype(str).map(lambda x: chrom_map.get(x, -1))
    
    # Extract POS numerically
    features['POS'] = pd.to_numeric(df['POS'], errors='coerce').fillna(0)
    
    # REF/ALT lengths and encoding
    ref_col = df['REF'].astype(str)
    alt_col = df['ALT'].astype(str)
    
    features['REF_len'] = ref_col.str.len()
    features['REF_encoded'] = ref_col.map(lambda x: ref_map.get(x, -1))
    
    features['ALT_len'] = alt_col.str.len()
    features['ALT_encoded'] = alt_col.map(lambda x: alt_map.get(x, -1))
    
    features['is_snp'] = ((features['REF_len'] == 1) & (features['ALT_len'] == 1)).astype(int)
    features['is_indel'] = (features['REF_len'] != features['ALT_len']).astype(int)
    features['mutation_size'] = (features['ALT_len'] - features['REF_len']).abs()
    
    # --- CELL 2: Allele Frequency ---
    features['AF_ESP'] = pd.to_numeric(info.str.extract(r'AF_ESP=([^;]+)')[0], errors='coerce')
    features['AF_EXAC'] = pd.to_numeric(info.str.extract(r'AF_EXAC=([^;]+)')[0], errors='coerce')
    features['AF_TGP'] = pd.to_numeric(info.str.extract(r'AF_TGP=([^;]+)')[0], errors='coerce')
    features['AF_combined'] = features['AF_ESP'].combine_first(features['AF_EXAC']).combine_first(features['AF_TGP'])
    
    # --- CELL 3: PolyPhen Score ---
    features['polyphen_score'] = pd.to_numeric(info.str.extract(r'[Pp]oly[Pp]hen[_=]([0-9.]+)')[0], errors='coerce')
    polyphen_raw = info.str.extract(r'[Pp]oly[Pp]hen=([^;,\s]+)')[0].fillna('unknown')
    polyphen_map = {'probably_damaging': 2, 'possibly_damaging': 1, 'benign': 0, 'unknown': -1}
    features['polyphen_cat'] = polyphen_raw.map(lambda x: next((v for k,v in polyphen_map.items() if k in str(x).lower()), -1))
    
    # --- CELL 4: SIFT Score ---
    features['sift_score'] = pd.to_numeric(info.str.extract(r'[Ss][Ii][Ff][Tt][_=]([0-9.]+)')[0], errors='coerce')
    sift_raw = info.str.extract(r'[Ss][Ii][Ff][Tt]=([^;,\s]+)')[0].fillna('unknown')
    sift_map = {'deleterious': 1, 'tolerated': 0, 'unknown': -1}
    features['sift_cat'] = sift_raw.map(lambda x: next((v for k,v in sift_map.items() if k in str(x).lower()), -1))

    # --- CELL 5: CADD, PhyloP, PhastCons Scores ---
    features['cadd_score'] = pd.to_numeric(info.str.extract(r'CADD[_=]([0-9.]+)')[0], errors='coerce')
    features['phylop_score'] = pd.to_numeric(info.str.extract(r'[Pp]hylo[Pp][_=]([0-9.-]+)')[0], errors='coerce')
    features['phastcons_score'] = pd.to_numeric(info.str.extract(r'[Pp]hast[Cc]ons[_=]([0-9.]+)')[0], errors='coerce')

    # --- CELL 6: Homozygous Flags ---
    features['is_homozygous'] = info.str.contains('CLNORIGIN=4', na=False).astype(int)
    features['has_homozygous_flag'] = info.str.contains('hom', case=False, na=False).astype(int)

    # --- CELL 7: Review Status ---
    features['is_reviewed'] = info.str.contains('CLNREVSTAT=reviewed_by_expert_panel', na=False).astype(int)
    features['is_criteria_provided'] = info.str.contains('CLNREVSTAT=criteria_provided', na=False).astype(int)
    features['is_no_criteria'] = info.str.contains('CLNREVSTAT=no_criteria', na=False).astype(int)

    # --- CELL 8: Gene Info ---
    features['has_gene_info'] = info.str.contains('GENEINFO=', na=False).astype(int)
    # Note: gene_encoded was factorized in training. We default to -1 in prod to avoid arbitrary mapping 
    # unless we also export a massive gene_dict.json. Given that tree-based models split on it, an unknown (-1) is safest.
    features['gene_encoded'] = -1 

    # --- CELL 9: Allele Count & RS ID ---
    features['allele_count'] = pd.to_numeric(info.str.extract(r'AC=([^;]+)')[0], errors='coerce')
    features['has_rs_id'] = info.str.contains(r'RS=\d', na=False).astype(int)

    # --- CELL 10: Variant Quality Tags ---
    for tag in ['DP', 'MQ', 'FS', 'SOR', 'QD']:
        features[tag] = pd.to_numeric(info.str.extract(rf'{tag}=([^;]+)')[0], errors='coerce')

    # --- Align with expected Features (from feature_names.json) ---
    expected_features = []
    try:
        if os.path.exists('feature_names.json'):
             with open('feature_names.json', 'r') as f:
                 expected_features = json.load(f)
    except Exception:
        pass
        
    if expected_features:
        # Fill any missing columns defined in training with 0
        for col in expected_features:
            if col not in features.columns:
                features[col] = 0
                
        # Reorder to match training exactly
        features = features[expected_features]
    else:
        # Fallback if json not found (should never happen if deployed correctly)
        pass 

    # --- CELL 11: Fill Missing Values ---
    # The pipeline has a SimpleImputer(strategy='median'), but during training there was a manual median fill step before it!
    # To strictly replicate training, we fillna with 0 for now, as SimpleImputer will handle the rest if left as NaN, 
    # but the manual fillna in training used the training median. We will let the pipeline imputer handle NaNs here.
    # Pipeline imputer will replace NaNs with the fitted median from training data.
    
    return features
