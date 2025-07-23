import pandas as pd
import re
import os

input_path = 'data/csv/recalls_2022_2025.csv'
output_path = 'data/csv/category_reasons.csv'

def load_data(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"The file {path} does not exist.")
    return pd.read_csv(path)

def clean_reasons(text):
    if pd.isna(text):
        return ''
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", '', text)  # Remove non-alphanumeric characters
    return text.strip()

import re

def categorize_reasons(reason: str) -> str:

    if any(k in reason for k in ["color change", "colour change","change in colour", "discoloration", "discolouration", "change of color", "pink to brown", "dark stains"]):
        return "color change"
    if any(k in reason for k in ["particles", "particulate", "precipitate", "black spots","Crystallization", "visible particles", "crystals", "brown crystals"]):
        return "particulate contamination"
    if any(k in reason for k in ["out of specification","Out-of-specification", "oos", "failure to comply", "failed assay", "not within specification"]):
        return "out of specification"
    if any(k in reason for k in ["market complaint", "complaint", "customer complaint", "reported"]):
        return "market complaints"
    if any(k in reason for k in ["leakage", "leaking", "bottle leak", "Sachets bloated", "can leak", "pinholes"]):
        return "leakage"
    if any(k in reason for k in ["mix up", "wrong label","Mislabeling", "wrong blister", "wrong packaging", "donystatin"]):
        return "mix-up"
    if any(k in reason for k in ["cracking", "lamination", "capping", "score line", "powdering", "crumbling"]):
        return "cracking / lamination"
    if any(k in reason for k in ["visual", "appearance", "white discoloration", "black spots", "dark brown"]):
        return "visual defect"
    if any(k in reason for k in ["mold", "mould", "microbial", "contamination"]):
        return "microbial contamination"
    if any(k in reason for k in ["corrosion", "corroded", "rust"]):
        return "corrosion"
    if any(k in reason for k in ["safety concern", "toxicity", "unacceptable level", "diethylene glycol"]):
        return "safety concern"
    if any(k in reason for k in ["packaging", "ampoule", "monocarton", "damaged box", "unit box", "blister damage"]):
        return "packaging defect"
    if any(k in reason for k in ["bitter taste", "strange taste"]):
        return "taste issue"
    if any(k in reason for k in ["market authorization", "registration", "unregistered"]):
        return "registration issue"
    
    return "Other"

    
def process_recalls(input_path, output_path):
        print(f"Loading data from {input_path}")
        df = load_data(input_path)

        df["clean_reasons"] = df["reason"].apply(clean_reasons)
        df["recall_category"] = df["clean_reasons"].apply(categorize_reasons)

        category_counts = df["recall_category"].value_counts().reset_index()
        category_counts.columns = ["recall_category", "count"]

        other_reasons = (
            df[df["recall_category"] == "Other"]["clean_reasons"]
            .value_counts()
            .head(20)
        )
        print("Top 20 'Other' reasons:")
        print(other_reasons)

        df[df["recall_category"] == "Other"][["reason"]].to_csv('data/csv/other_reasons.csv', index=False)

        category_counts.to_csv(output_path, index=False)
        print(f"Processed {len(df)} recalls and saved category counts to {output_path}")

if __name__ == "__main__":
            process_recalls(input_path, output_path)