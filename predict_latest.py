#!/usr/bin/env python3
"""
Kidney Disease Prediction Pipeline
===================================
This script fetches the latest patient data from the API,
loads the trained ML model, makes a prediction, and saves
the diagnosis back to the database.

Author: Group 12
Date: November 2025
"""

import os
import sys
import requests
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Tuple, Optional

# ============================================
# Configuration
# ============================================

API_BASE_URL = "http://localhost:8000"
MODEL_PATH = "models/kidney_disease_rf_model.joblib"
FEATURE_NAMES_PATH = "models/feature_names.joblib"
METADATA_PATH = "models/model_metadata.joblib"

# Required features in correct order for the model
REQUIRED_FEATURES = ['Age', 'Creatinine_Level', 'BUN', 'GFR', 'Urine_Output', 'Diabetes', 'Hypertension']

# ============================================
# Helper Functions
# ============================================

def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_section(text: str):
    """Print a formatted section header."""
    print(f"\n{'-' * 70}")
    print(f"  {text}")
    print(f"{'-' * 70}")

def print_success(text: str):
    """Print success message."""
    print(f"[OK] {text}")

def print_error(text: str):
    """Print error message."""
    print(f"[ERROR] {text}")

def print_info(key: str, value):
    """Print key-value information."""
    print(f"  - {key}: {value}")

# ============================================
# Model Loading
# ============================================

def load_model() -> Tuple[object, list, dict]:
    """
    Load the trained ML model and metadata.

    Returns:
        Tuple of (model, feature_names, metadata)
    """
    print_section("Loading ML Model")

    try:
        # Check if model files exist
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
        if not os.path.exists(FEATURE_NAMES_PATH):
            raise FileNotFoundError(f"Feature names file not found: {FEATURE_NAMES_PATH}")
        if not os.path.exists(METADATA_PATH):
            raise FileNotFoundError(f"Metadata file not found: {METADATA_PATH}")

        # Load model files
        model = joblib.load(MODEL_PATH)
        feature_names = joblib.load(FEATURE_NAMES_PATH)
        metadata = joblib.load(METADATA_PATH)

        print_success("Model loaded successfully")
        print_info("Model Type", metadata.get('model_type', 'Unknown'))
        print_info("Accuracy", f"{metadata.get('accuracy', 0) * 100:.2f}%")
        print_info("Features", len(feature_names))
        print_info("Training Date", metadata.get('training_date', 'Unknown'))

        return model, feature_names, metadata

    except Exception as e:
        print_error(f"Failed to load model: {str(e)}")
        sys.exit(1)

# ============================================
# API Functions
# ============================================

def fetch_latest_patient() -> Optional[Dict]:
    """
    Fetch the latest patient data from the API.

    Returns:
        Patient data dictionary or None if failed
    """
    print_section("Fetching Latest Patient Data")

    try:
        # First, get the latest patient
        response = requests.get(f"{API_BASE_URL}/patients/latest", timeout=10)

        if response.status_code == 404:
            print_error("No patients found in database")
            return None

        response.raise_for_status()
        patient = response.json()

        patient_id = patient.get('Patient_ID')
        print_success(f"Patient fetched: ID #{patient_id}")
        print_info("Name", patient.get('Name', 'N/A'))
        print_info("Age", patient.get('Age', 'N/A'))
        print_info("Gender", patient.get('Gender', 'N/A'))

        # Fetch medical history
        history_response = requests.get(f"{API_BASE_URL}/history/{patient_id}", timeout=10)
        history_response.raise_for_status()
        history = history_response.json()

        # Fetch lab results
        labs_response = requests.get(f"{API_BASE_URL}/labs/{patient_id}", timeout=10)
        labs_response.raise_for_status()
        labs = labs_response.json()

        if not history or not labs:
            print_error("Patient missing medical history or lab results")
            return None

        # Get the most recent records
        latest_history = history[0] if isinstance(history, list) else history
        latest_labs = labs[-1] if isinstance(labs, list) else labs  # Most recent labs

        # Combine all data
        complete_data = {
            **patient,
            'Diabetes': latest_history.get('Diabetes'),
            'Hypertension': latest_history.get('Hypertension'),
            'Creatinine_Level': latest_labs.get('Creatinine_Level'),
            'BUN': latest_labs.get('BUN_Level'),
            'GFR': latest_labs.get('GFR_Value'),
            'Urine_Output': latest_labs.get('Urine_Output'),
            'Test_Date': latest_labs.get('Test_Date')
        }

        print_success("Medical history and lab results retrieved")

        return complete_data

    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API. Is the server running?")
        print_info("Start server", "cd kidney_api/sql_api && uvicorn main:app --reload")
        return None
    except requests.exceptions.Timeout:
        print_error("API request timed out")
        return None
    except requests.exceptions.RequestException as e:
        print_error(f"API request failed: {str(e)}")
        return None
    except Exception as e:
        print_error(f"Unexpected error fetching patient: {str(e)}")
        return None

def save_diagnosis(patient_id: int, ckd_status: bool, risk_score: float) -> bool:
    """
    Save the diagnosis to the database via API.

    Args:
        patient_id: Patient ID
        ckd_status: CKD diagnosis (True/False)
        risk_score: Probability score (0-1)

    Returns:
        True if successful, False otherwise
    """
    print_section("Saving Diagnosis to Database")

    try:
        diagnosis_data = {
            "Patient_ID": patient_id,
            "CKD_Status": ckd_status,
            "Risk_Score": float(risk_score),
            "Diagnosed_By": "KidneyAI ML Model",
            "Model_Version": "RandomForest_v1.0"
        }

        response = requests.post(
            f"{API_BASE_URL}/diagnoses",
            json=diagnosis_data,
            timeout=10
        )
        response.raise_for_status()

        result = response.json()
        diagnosis_id = result.get('Diagnosis_ID')

        print_success(f"Diagnosis saved successfully (ID: #{diagnosis_id})")
        print_info("Trigger activated", "Diagnosis logged to audit table")

        return True

    except requests.exceptions.RequestException as e:
        print_error(f"Failed to save diagnosis: {str(e)}")
        return False
    except Exception as e:
        print_error(f"Unexpected error saving diagnosis: {str(e)}")
        return False

# ============================================
# Data Preprocessing
# ============================================

def prepare_features(patient_data: Dict, feature_names: list) -> Optional[pd.DataFrame]:
    """
    Prepare patient data for model prediction.

    Args:
        patient_data: Raw patient data from API
        feature_names: List of required feature names

    Returns:
        DataFrame ready for prediction or None if data is invalid
    """
    print_section("Preparing Data for Prediction")

    try:
        # Extract features in correct order
        features = {}

        # Map database field names to model feature names
        field_mapping = {
            'Age': 'Age',
            'Creatinine_Level': 'Creatinine_Level',
            'BUN': 'BUN',
            'GFR': 'GFR',
            'Urine_Output': 'Urine_Output',
            'Diabetes': 'Diabetes',
            'Hypertension': 'Hypertension'
        }

        # Extract and validate each feature
        for model_feature, data_field in field_mapping.items():
            value = patient_data.get(data_field)

            if value is None:
                print_error(f"Missing required field: {data_field}")
                return None

            # Convert boolean to int for ML model
            if isinstance(value, bool):
                value = int(value)

            features[model_feature] = value

        # Create DataFrame
        df = pd.DataFrame([features])

        # Ensure columns are in correct order
        df = df[feature_names]

        print_success("Features prepared successfully")
        print("\nFeature Values:")
        for feature in feature_names:
            value = df[feature].values[0]
            print_info(feature, value)

        return df

    except Exception as e:
        print_error(f"Failed to prepare features: {str(e)}")
        return None

# ============================================
# Prediction
# ============================================

def make_prediction(model, features: pd.DataFrame) -> Tuple[int, float, np.ndarray]:
    """
    Make CKD prediction using the trained model.

    Args:
        model: Trained ML model
        features: Prepared feature DataFrame

    Returns:
        Tuple of (prediction, risk_score, probabilities)
    """
    print_section("Making Prediction")

    try:
        # Get prediction
        prediction = model.predict(features)[0]

        # Get probability scores
        probabilities = model.predict_proba(features)[0]

        # Risk score is probability of positive class
        risk_score = probabilities[1]

        print_success("Prediction completed")

        return int(prediction), float(risk_score), probabilities

    except Exception as e:
        print_error(f"Prediction failed: {str(e)}")
        sys.exit(1)

# ============================================
# Results Display
# ============================================

def display_results(patient_data: Dict, prediction: int, risk_score: float, probabilities: np.ndarray):
    """
    Display prediction results in a formatted way.

    Args:
        patient_data: Original patient data
        prediction: CKD prediction (0 or 1)
        risk_score: Risk probability
        probabilities: Class probabilities
    """
    print_header("PREDICTION RESULTS")

    # Patient Information
    print("\n[PATIENT INFORMATION]")
    print_info("ID", patient_data.get('Patient_ID'))
    print_info("Name", patient_data.get('Name'))
    print_info("Age", patient_data.get('Age'))
    print_info("Gender", patient_data.get('Gender'))

    # Lab Values
    print("\n[LABORATORY VALUES]")
    print_info("Creatinine", f"{patient_data.get('Creatinine_Level')} mg/dL")
    print_info("BUN", f"{patient_data.get('BUN')} mg/dL")
    print_info("GFR", f"{patient_data.get('GFR')} mL/min")
    print_info("Urine Output", f"{patient_data.get('Urine_Output')} mL/day")

    # Medical History
    print("\n[MEDICAL HISTORY]")
    print_info("Diabetes", "Yes" if patient_data.get('Diabetes') else "No")
    print_info("Hypertension", "Yes" if patient_data.get('Hypertension') else "No")

    # Prediction
    print("\n[PREDICTION]")
    ckd_status = "CKD DETECTED" if prediction == 1 else "NO CKD DETECTED"
    status_symbol = "[WARNING]" if prediction == 1 else "[OK]"

    print(f"\n  {status_symbol}  STATUS: {ckd_status}")
    print(f"  Risk Score: {risk_score * 100:.2f}%")
    print(f"  Confidence: {max(probabilities) * 100:.2f}%")

    # Risk Level
    if risk_score < 0.3:
        risk_level = "LOW RISK"
        recommendation = "Continue regular health monitoring"
    elif risk_score < 0.7:
        risk_level = "MODERATE RISK"
        recommendation = "Increased monitoring recommended"
    else:
        risk_level = "HIGH RISK"
        recommendation = "Immediate medical attention recommended"

    print(f"\n  Risk Level: {risk_level}")
    print(f"  Recommendation: {recommendation}")

    # Feature Importance Context
    print("\n[KEY INDICATORS (by importance)]")
    print_info("GFR (60% weight)", f"{patient_data.get('GFR')} mL/min" +
               (" - Critical" if patient_data.get('GFR') < 30 else
                " - Low" if patient_data.get('GFR') < 60 else " - Normal"))
    print_info("BUN (23% weight)", f"{patient_data.get('BUN')} mg/dL" +
               (" - Elevated" if patient_data.get('BUN') > 40 else
                " - High Normal" if patient_data.get('BUN') > 20 else " - Normal"))
    print_info("Creatinine (13% weight)", f"{patient_data.get('Creatinine_Level')} mg/dL" +
               (" - High" if patient_data.get('Creatinine_Level') > 2.0 else
                " - Borderline" if patient_data.get('Creatinine_Level') > 1.3 else " - Normal"))

# ============================================
# Main Execution
# ============================================

def main():
    """Main execution function."""

    print_header("KIDNEY DISEASE PREDICTION PIPELINE")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: Load ML Model
    model, feature_names, metadata = load_model()

    # Step 2: Fetch Latest Patient
    patient_data = fetch_latest_patient()
    if patient_data is None:
        print_error("Cannot proceed without patient data")
        sys.exit(1)

    # Step 3: Prepare Features
    features = prepare_features(patient_data, feature_names)
    if features is None:
        print_error("Cannot proceed with invalid features")
        sys.exit(1)

    # Step 4: Make Prediction
    prediction, risk_score, probabilities = make_prediction(model, features)

    # Step 5: Display Results
    display_results(patient_data, prediction, risk_score, probabilities)

    # Step 6: Save Diagnosis
    patient_id = patient_data.get('Patient_ID')
    ckd_status = bool(prediction)
    success = save_diagnosis(patient_id, ckd_status, risk_score)

    if success:
        print_header("PREDICTION PIPELINE COMPLETED SUCCESSFULLY")
        print_success("All tasks completed")
        print_info("Patient diagnosed", patient_data.get('Name'))
        print_info("Diagnosis saved to", "MySQL database")
        print_info("Audit log created", "Diagnosis_Log table")
        print("\n")
    else:
        print_error("Failed to save diagnosis to database")
        sys.exit(1)

# ============================================
# Entry Point
# ============================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
