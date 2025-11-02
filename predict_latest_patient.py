"""
Kidney Disease Prediction Script
Task 3: Fetch Data for Prediction

This script:
1. Fetches the latest patient data from the API
2. Loads the trained Random Forest model
3. Prepares the data for prediction
4. Makes a prediction and saves it to the database
"""

import requests
import joblib
import numpy as np
import pandas as pd
from datetime import date, datetime
import sys

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Model paths
MODEL_PATH = "models/kidney_disease_rf_model.joblib"
FEATURE_NAMES_PATH = "models/feature_names.joblib"
METADATA_PATH = "models/model_metadata.joblib"


def check_api_connection():
    """Check if the API is running and accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            print(" API connection successful!")
            print(f"   API Status: {response.json()}")
            return True
        else:
            print(f" API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(" Cannot connect to API. Make sure the API is running on http://localhost:8000")
        print("   Run: python kidney_disease_crud_api.py")
        return False
    except Exception as e:
        print(f" Error checking API connection: {e}")
        return False


def load_ml_model():
    """Load the trained Random Forest model and related files"""
    try:
        print("\n Loading ML model...")
        model = joblib.load(MODEL_PATH)
        feature_names = joblib.load(FEATURE_NAMES_PATH)
        metadata = joblib.load(METADATA_PATH)
        
        print(f"   Model loaded successfully!")
        print(f"   Model Type: {metadata.get('model_type', 'Random Forest')}")
        print(f"   Accuracy: {metadata.get('accuracy', 'N/A')}")
        print(f"   Features: {', '.join(feature_names)}")
        
        return model, feature_names, metadata
    except FileNotFoundError as e:
        print(f"  Model file not found: {e}")
        print("   Make sure the model files exist in the 'models/' directory")
        return None, None, None
    except Exception as e:
        print(f"  Error loading model: {e}")
        return None, None, None


def fetch_latest_patient_data():
    """Fetch the latest patient with all medical data from the API"""
    try:
        print("\n  Fetching latest patient data from API...")
        response = requests.get(f"{API_BASE_URL}/mysql/patients/latest/full-data")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Patient data fetched successfully!")
            print(f"   Patient: {data['patient']['Name']}")
            print(f"   Age: {data['patient']['Age']} years")
            print(f"   Patient ID: {data['patient']['Patient_ID']}")
            return data
        elif response.status_code == 404:
            print("  No patients found in database")
            return None
        else:
            print(f" Failed to fetch data: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f" Error fetching patient data: {e}")
        return None


def prepare_features_for_prediction(patient_data, feature_names):
    """
    Extract and prepare features for ML model prediction
    
    Args:
        patient_data: Dictionary containing patient, medical_history, and lab_results
        feature_names: List of feature names expected by the model
    
    Returns:
        DataFrame with prepared features, Patient ID, and patient name
    """
    try:
        print("\n  Preparing features for prediction...")
        
        # Extract data from API response
        patient = patient_data['patient']
        medical_history = patient_data['medical_history']
        lab_results = patient_data['lab_results']
        
        # Create feature dictionary matching the model's training features
        # Note: Model was trained with these exact column names from the notebook
        features = {
            'Age': patient['Age'],
            'Creatinine_Level': lab_results['Creatinine_Level'],
            'BUN': lab_results['BUN_Level'],  # Model expects 'BUN' not 'BUN_Level'
            'GFR': lab_results['GFR_Value'],  # Model expects 'GFR' not 'GFR_Value'
            'Urine_Output': lab_results['Urine_Output'],
            'Diabetes': int(medical_history['Diabetes']),
            'Hypertension': int(medical_history['Hypertension'])
        }
        
        # Display the features
        print("   Features extracted:")
        for feature_name, value in features.items():
            print(f"     • {feature_name}: {value}")
        
        # Convert to DataFrame with correct feature order
        df = pd.DataFrame([features])
        
        # Ensure features are in the correct order for the model
        df = df[feature_names]
        
        print(" Features prepared successfully!")
        
        return df, patient['Patient_ID'], patient['Name']
    
    except KeyError as e:
        print(f"  Missing required field in patient data: {e}")
        return None, None, None
    except Exception as e:
        print(f" Error preparing features: {e}")
        return None, None, None


def make_prediction(model, features_df):
    """
    Make prediction using the trained ML model
    
    Args:
        model: Trained Random Forest model
        features_df: DataFrame with prepared features
    
    Returns:
        Dictionary with prediction results
    """
    try:
        print("\n Making prediction...")
        
        # Get prediction (0 = No CKD, 1 = CKD)
        prediction = model.predict(features_df)[0]
        
        # Get prediction probabilities [probability of No CKD, probability of CKD]
        probabilities = model.predict_proba(features_df)[0]
        
        # Calculate risk score and confidence
        risk_score = float(probabilities[1])  # Probability of having CKD
        confidence = float(max(probabilities))  # Confidence in the prediction
        
        result = {
            'ckd_status': bool(prediction),  # True if CKD detected, False otherwise
            'risk_score': risk_score,
            'confidence': confidence,
            'ckd_probability': risk_score,
            'no_ckd_probability': float(probabilities[0])
        }
        
        print(" Prediction completed!")
        print(f"\n PREDICTION RESULTS:")
        print(f"   {'='*50}")
        print(f"   CKD Status: {'POSITIVE ' if result['ckd_status'] else 'NEGATIVE ✓'}")
        print(f"   Risk Score: {result['risk_score']:.4f} ({result['risk_score']*100:.2f}%)")
        print(f"   Confidence: {result['confidence']:.4f} ({result['confidence']*100:.2f}%)")
        print(f"   {'='*50}")
        print(f"   Probability Breakdown:")
        print(f"     • CKD Positive: {result['ckd_probability']*100:.2f}%")
        print(f"     • CKD Negative: {result['no_ckd_probability']*100:.2f}%")
        print(f"   {'='*50}")
        
        # Interpret the risk level
        if result['risk_score'] >= 0.8:
            risk_level = "HIGH RISK"
        elif result['risk_score'] >= 0.5:
            risk_level = "MODERATE RISK"
        else:
            risk_level = "LOW RISK"
        
        print(f"   Risk Level: {risk_level}")
        print(f"   {'='*50}\n")
        
        return result
    
    except Exception as e:
        print(f" Error making prediction: {e}")
        return None


def save_prediction_to_database(patient_id, patient_name, prediction_result, metadata):
    """
    Save prediction results back to the database via API
    
    Args:
        patient_id: ID of the patient
        patient_name: Name of the patient
        prediction_result: Dictionary with prediction results
        metadata: Model metadata
    """
    try:
        print(" Saving prediction to MySQL database...")
        
        # Prepare diagnosis data as query parameters
        params = {
            "patient_id": patient_id,
            "ckd_status": prediction_result['ckd_status'],
            "risk_score": round(prediction_result['risk_score'], 4),
            "diagnosed_by": "ML Random Forest Model",
            "diagnosis_date": str(date.today()),
            "model_version": f"RandomForest_Accuracy_{metadata.get('accuracy', 1.0)}"
        }
        
        # Send POST request to save diagnosis with query parameters
        response = requests.post(
            f"{API_BASE_URL}/mysql/diagnoses/",
            params=params
        )
        
        if response.status_code == 200:
            print(" Prediction saved to MySQL successfully!")
            saved_data = response.json()
            print(f"   Diagnosis ID: {saved_data.get('Diagnosis_ID', 'N/A')}")
            return saved_data
        else:
            print(f" Failed to save prediction: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    
    except Exception as e:
        print(f" Error saving prediction to MySQL: {e}")
        return None


def log_prediction_to_mongodb(patient_id, patient_name, prediction_result, patient_data, metadata):
    """
    Log prediction details to MongoDB for audit trail
    
    Args:
        patient_id: ID of the patient
        patient_name: Name of the patient
        prediction_result: Dictionary with prediction results
        patient_data: Original patient data used for prediction
        metadata: Model metadata
    """
    try:
        print(" Logging prediction to MongoDB...")
        
        # Prepare log entry
        log_entry = {
            "patient_id": patient_id,
            "patient_name": patient_name,
            "prediction": "CKD Positive" if prediction_result['ckd_status'] else "CKD Negative",
            "ckd_status": prediction_result['ckd_status'],
            "risk_score": prediction_result['risk_score'],
            "confidence": prediction_result['confidence'],
            "ckd_probability": prediction_result['ckd_probability'],
            "no_ckd_probability": prediction_result['no_ckd_probability'],
            "input_features": patient_data,
            "model_version": f"RandomForest_Accuracy_{metadata.get('accuracy', 1.0)}",
            "model_type": metadata.get('model_type', 'RandomForestClassifier'),
            "prediction_date": datetime.now().isoformat(),
            "source": "predict_latest_patient.py script",
            "assignment_task": "Task 3 - Fetch and Predict"
        }
        
        # Send POST request to MongoDB prediction logs collection
        response = requests.post(
            f"{API_BASE_URL}/mongodb/prediction-logs/",
            json=log_entry
        )
        
        if response.status_code == 200:
            print(" Prediction logged to MongoDB successfully!")
            return response.json()
        else:
            print(f" MongoDB logging failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    
    except Exception as e:
        print(f" Error logging to MongoDB: {e}")
        print("   (Continuing without MongoDB log)")
        return None


def main():
    """Main prediction workflow"""
    print("\n" + "="*70)
    print(" KIDNEY DISEASE PREDICTION SYSTEM")
    print("="*70)
    print("Task 3: Fetch Data for Prediction & Make Predictions")
    print("="*70 + "\n")
    
    # Step 1: Check API connection
    if not check_api_connection():
        print("\n Cannot proceed without API connection.")
        print(" Please start the API first: python kidney_disease_api.py")
        sys.exit(1)
    
    # Step 2: Load ML model
    model, feature_names, metadata = load_ml_model()
    if model is None:
        print("\n Cannot proceed without ML model.")
        sys.exit(1)
    
    # Step 3: Fetch latest patient data
    patient_data = fetch_latest_patient_data()
    if patient_data is None:
        print("\n Cannot proceed without patient data.")
        sys.exit(1)
    
    # Step 4: Prepare features for prediction
    features_df, patient_id, patient_name = prepare_features_for_prediction(
        patient_data, feature_names
    )
    if features_df is None:
        print("\n Cannot proceed without prepared features.")
        sys.exit(1)
    
    # Step 5: Make prediction
    prediction_result = make_prediction(model, features_df)
    if prediction_result is None:
        print("\n Prediction failed.")
        sys.exit(1)
    
    # Step 6: Save prediction to MySQL database
    saved_result = save_prediction_to_database(
        patient_id, patient_name, prediction_result, metadata
    )
    
    # Step 7: Log prediction to MongoDB for audit trail
    mongo_log = log_prediction_to_mongodb(
        patient_id, patient_name, prediction_result, 
        features_df.to_dict('records')[0], metadata
    )
    
    # Final summary
    print("\n" + "="*70)
    print(" PREDICTION WORKFLOW COMPLETED SUCCESSFULLY!")
    print("="*70)
    print(f"Patient: {patient_name} (ID: {patient_id})")
    print(f"Prediction: {'CKD POSITIVE' if prediction_result['ckd_status'] else 'CKD NEGATIVE'}")
    print(f"Risk Score: {prediction_result['risk_score']*100:.2f}%")
    print(f"\n Database Status:")
    print(f"   MySQL (Structured Data): {'✓ Saved' if saved_result else '✗ Failed'}")
    print(f"   MongoDB (Audit Log): {'✓ Logged' if mongo_log else '✗ Failed'}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
