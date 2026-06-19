from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import json
import os
from backend_utils import parse_vcf_text, extract_features_prod

app = Flask(__name__)

# Load model and feature names globally
MODEL_PATH = "best_model.pkl"
FEATURE_NAMES_PATH = "feature_names.json"

model = None
feature_names = None

try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print("✅ Model loaded successfully!")
    else:
        print("⚠️ Warning: best_model.pkl not found. Please run the Jupyter cell to save the model.")
        
    if os.path.exists(FEATURE_NAMES_PATH):
        with open(FEATURE_NAMES_PATH, "r") as f:
            feature_names = json.load(f)
        print("✅ Feature names loaded successfully!")
except Exception as e:
    print(f"Error loading model/features: {e}")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded. Please save best_model.pkl from the Jupyter notebook."}), 500

    try:
        data = request.get_json()
        if not data or "vcf_data" not in data:
            return jsonify({"error": "No VCF data provided"}), 400

        vcf_text = data["vcf_data"]
        
        # 1. Parse VCF string into DataFrame
        df_vcf = parse_vcf_text(vcf_text)
        if df_vcf.empty:
            return jsonify({"error": "Could not parse VCF data. Please ensure it is correctly formatted."}), 400

        # 2. Extract features exactly as the model expects
        features_df = extract_features_prod(df_vcf)
        
        # If the feature dataframe is completely empty due to a parsing error
        if features_df.empty:
            return jsonify({"error": "Failed to extract features from VCF data."}), 400

        # 3. Predict using the loaded model pipeline
        # The model is a pipeline: SimpleImputer -> StandardScaler -> Classifier
        predictions = model.predict(features_df)
        probabilities = model.predict_proba(features_df)

        # 4. Format results
        results = []
        for i in range(len(predictions)):
            # Probability array is usually [prob_benign, prob_pathogenic]
            # Verify the order based on standard sklearn classes
            prob_pathogenic = probabilities[i][1] if len(probabilities[i]) > 1 else probabilities[i][0]
            
            label = "Pathogenic" if predictions[i] == 1 else "Benign"
            confidence = f"{prob_pathogenic * 100:.2f}%" if label == "Pathogenic" else f"{(1 - prob_pathogenic) * 100:.2f}%"

            results.append({
                "index": i + 1,
                "prediction": label,
                "confidence": confidence,
                "raw_prob_pathogenic": float(prob_pathogenic)
            })

        return jsonify({
            "message": f"Successfully processed {len(results)} variant(s).",
            "results": results,
            "summary": {
                "total": len(results),
                "pathogenic": sum(1 for r in results if r["prediction"] == "Pathogenic"),
                "benign": sum(1 for r in results if r["prediction"] == "Benign")
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)