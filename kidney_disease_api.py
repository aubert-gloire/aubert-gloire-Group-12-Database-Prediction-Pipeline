from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DECIMAL, Date, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import joblib
import numpy as np
import pandas as pd
import os
import motor.motor_asyncio
from bson import ObjectId
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# DATABASE CONFIGURATIONS (Using Environment Variables)
# ============================================================================

# MySQL Configuration (from environment variables)
MYSQL_URL = os.getenv("MYSQL_URL")
if not MYSQL_URL:
    # Fallback: construct from individual components if needed
    mysql_host = os.getenv("MYSQL_HOST")
    mysql_port = os.getenv("MYSQL_PORT", "3306")
    mysql_user = os.getenv("MYSQL_USER")
    mysql_password = os.getenv("MYSQL_PASSWORD")
    mysql_database = os.getenv("MYSQL_DATABASE", "defaultdb")
    
    if all([mysql_host, mysql_user, mysql_password]):
        MYSQL_URL = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"

# MongoDB Atlas Configuration (from environment variables)
MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    # Fallback: construct from individual components if needed
    mongodb_user = os.getenv("MONGODB_USERNAME")
    mongodb_password = os.getenv("MONGODB_PASSWORD")
    mongodb_cluster = os.getenv("MONGODB_CLUSTER")
    mongodb_app_name = os.getenv("MONGODB_APP_NAME", "Cluster0")
    
    if all([mongodb_user, mongodb_password, mongodb_cluster]):
        MONGODB_URL = f"mongodb+srv://{mongodb_user}:{mongodb_password}@{mongodb_cluster}/?appName={mongodb_app_name}"

MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "hospital_db")

# Initialize MySQL
try:
    if MYSQL_URL:
        mysql_engine = create_engine(MYSQL_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mysql_engine)
        Base = declarative_base()
        print("MySQL connection configured successfully!")
    else:
        print("MySQL URL not configured in environment variables")
        mysql_engine = None
        SessionLocal = None
except Exception as e:
    print(f"MySQL connection failed: {e}")
    mysql_engine = None
    SessionLocal = None

# Initialize MongoDB Atlas
try:
    if MONGODB_URL:
        mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
        mongodb_db = mongodb_client[MONGODB_DATABASE]
        print("MongoDB Atlas connection configured successfully!")
    else:
        print("MongoDB URL not configured in environment variables")
        mongodb_client = None
        mongodb_db = None
except Exception as e:
    print(f"MongoDB Atlas connection failed: {e}")
    mongodb_client = None
    mongodb_db = None

# ============================================================================
# ML MODEL LOADING
# ============================================================================

# Load Random Forest model (with configurable paths from environment)
try:
    model_path = os.getenv("MODEL_PATH", "models/kidney_disease_rf_model.joblib")
    feature_names_path = os.getenv("FEATURE_NAMES_PATH", "models/feature_names.joblib")
    metadata_path = os.getenv("METADATA_PATH", "models/model_metadata.joblib")
    
    if all(os.path.exists(p) for p in [model_path, feature_names_path, metadata_path]):
        ml_model = joblib.load(model_path)
        feature_names = joblib.load(feature_names_path)
        model_metadata = joblib.load(metadata_path)
        print("ML Model loaded successfully!")
        print(f"   Model Accuracy: {model_metadata.get('accuracy', 0)*100:.2f}%")
    else:
        print("ML Model files not found!")
        ml_model = None
        feature_names = None
        model_metadata = None
except Exception as e:
    print(f"ML Model loading failed: {e}")
    ml_model = None
    feature_names = None
    model_metadata = None

# ============================================================================
# SQLALCHEMY MODELS (MySQL)
# ============================================================================

class Patient(Base):
    __tablename__ = "Patients"
    
    Patient_ID = Column(Integer, primary_key=True, index=True)
    Name = Column(String(100))
    Age = Column(Integer)
    Gender = Column(String(10))
    Email = Column(String(255), unique=True)
    Phone = Column(String(20))

class MedicalHistory(Base):
    __tablename__ = "Medical_History"
    
    History_ID = Column(Integer, primary_key=True, index=True)
    Patient_ID = Column(Integer)
    Diabetes = Column(Boolean, default=False)
    Hypertension = Column(Boolean, default=False)
    Record_Date = Column(Date)

class LabResults(Base):
    __tablename__ = "Lab_Results"
    
    Lab_ID = Column(Integer, primary_key=True, index=True)
    Patient_ID = Column(Integer)
    Creatinine_Level = Column(DECIMAL(5,2))
    BUN_Level = Column(DECIMAL(5,2))
    GFR_Value = Column(DECIMAL(5,2))
    Urine_Output = Column(DECIMAL(8,2))
    Test_Date = Column(Date)

class Diagnosis(Base):
    __tablename__ = "Diagnoses"
    
    Diagnosis_ID = Column(Integer, primary_key=True, index=True)
    Patient_ID = Column(Integer)
    CKD_Status = Column(Boolean)
    Risk_Score = Column(DECIMAL(5,4))
    Diagnosed_By = Column(String(100))
    Diagnosis_Date = Column(Date)
    Model_Version = Column(String(50))

# ============================================================================
# PYDANTIC MODELS (API Schemas)
# ============================================================================

class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    email: str
    phone: str

class PatientResponse(BaseModel):
    Patient_ID: int
    Name: str
    Age: int
    Gender: str
    Email: str
    Phone: str

class MLPredictionRequest(BaseModel):
    Age: int
    Creatinine_Level: float
    BUN_Level: float
    GFR_Value: float
    Urine_Output: float
    Diabetes: bool
    Hypertension: bool

class MLPredictionResponse(BaseModel):
    prediction: str
    ckd_status: bool
    risk_score: float
    confidence: float
    patient_id: Optional[int] = None
    prediction_date: str
    model_version: str

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Kidney Disease Prediction API",
    description="Complete database assignment with dual database support and ML integration",
    version="1.0.0"
)

# CORS middleware (configurable origins)
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_mysql_db():
    if SessionLocal is None:
        raise HTTPException(status_code=500, detail="MySQL database not available")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/", tags=["Health Check"])
async def health_check():
    """Health check endpoint showing system status"""
    return {
        "message": "Kidney Disease Prediction API - Dual Database Support",
        "version": "1.0.0",
        "status": {
            "mysql_available": mysql_engine is not None,
            "mongodb_available": mongodb_client is not None,
            "ml_model_loaded": ml_model is not None
        },
        "databases": {
            "mysql": "Available" if mysql_engine else "Unavailable",
            "mongodb": "Available" if mongodb_client else "Unavailable"
        },
        "ml_model": {
            "loaded": ml_model is not None,
            "accuracy": f"{model_metadata.get('accuracy', 0)*100:.2f}%" if model_metadata else "N/A"
        },
        "endpoints": {
            "mysql_crud": "/mysql/patients/",
            "mongodb_crud": "/mongodb/patients/",
            "ml_prediction": "/predict/",
            "predict_latest": "/predict-latest",
            "documentation": "/docs"
        }
    }

# ============================================================================
# MYSQL CRUD ENDPOINTS
# ============================================================================

@app.post("/mysql/patients/", response_model=PatientResponse, tags=["MySQL - Patients"])
def create_patient_mysql(patient: PatientCreate, db: Session = Depends(get_mysql_db)):
    """Create a new patient in MySQL database"""
    try:
        db_patient = Patient(
            Name=patient.name,
            Age=patient.age,
            Gender=patient.gender,
            Email=patient.email,
            Phone=patient.phone
        )
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        return db_patient
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating patient: {str(e)}")

@app.get("/mysql/patients/", response_model=List[PatientResponse], tags=["MySQL - Patients"])
def get_patients_mysql(db: Session = Depends(get_mysql_db)):
    """Get all patients from MySQL database"""
    patients = db.query(Patient).all()
    return patients

@app.get("/mysql/patients/{patient_id}", response_model=PatientResponse, tags=["MySQL - Patients"])
def get_patient_mysql(patient_id: int, db: Session = Depends(get_mysql_db)):
    """Get specific patient from MySQL database"""
    patient = db.query(Patient).filter(Patient.Patient_ID == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.put("/mysql/patients/{patient_id}", response_model=PatientResponse, tags=["MySQL - Patients"])
def update_patient_mysql(patient_id: int, patient: PatientCreate, db: Session = Depends(get_mysql_db)):
    """Update patient in MySQL database"""
    db_patient = db.query(Patient).filter(Patient.Patient_ID == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    for key, value in patient.dict().items():
        setattr(db_patient, key.title(), value)
    
    db.commit()
    db.refresh(db_patient)
    return db_patient

@app.delete("/mysql/patients/{patient_id}", tags=["MySQL - Patients"])
def delete_patient_mysql(patient_id: int, db: Session = Depends(get_mysql_db)):
    """Delete patient from MySQL database"""
    patient = db.query(Patient).filter(Patient.Patient_ID == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    db.delete(patient)
    db.commit()
    return {"message": f"Patient {patient_id} deleted successfully"}

# ============================================================================
# MONGODB CRUD ENDPOINTS
# ============================================================================

@app.post("/mongodb/patients/", tags=["MongoDB - Patients"])
async def create_patient_mongodb(patient: PatientCreate):
    """Create a new patient in MongoDB Atlas"""
    if mongodb_db is None:
        raise HTTPException(status_code=500, detail="MongoDB not available")
    
    try:
        # Get next patient_id
        last_patient = await mongodb_db.patients.find_one(sort=[("patient_id", -1)])
        next_id = (last_patient["patient_id"] + 1) if last_patient else 1
        
        patient_doc = {
            "patient_id": next_id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "email": patient.email,
            "phone": patient.phone,
            "created_at": datetime.now()
        }
        
        result = await mongodb_db.patients.insert_one(patient_doc)
        patient_doc["_id"] = str(result.inserted_id)
        return {"message": "Patient created successfully", "patient": patient_doc}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating patient: {str(e)}")

@app.get("/mongodb/patients/", tags=["MongoDB - Patients"])
async def get_patients_mongodb():
    """Get all patients from MongoDB Atlas"""
    if mongodb_db is None:
        raise HTTPException(status_code=500, detail="MongoDB not available")
    
    try:
        patients = []
        async for patient in mongodb_db.patients.find():
            patient["_id"] = str(patient["_id"])
            patients.append(patient)
        return {"patients": patients, "count": len(patients)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching patients: {str(e)}")

@app.get("/mongodb/patients/{patient_id}", tags=["MongoDB - Patients"])
async def get_patient_mongodb(patient_id: int):
    """Get specific patient from MongoDB Atlas"""
    if mongodb_db is None:
        raise HTTPException(status_code=500, detail="MongoDB not available")
    
    try:
        patient = await mongodb_db.patients.find_one({"patient_id": patient_id})
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        patient["_id"] = str(patient["_id"])
        return {"patient": patient}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching patient: {str(e)}")

@app.put("/mongodb/patients/{patient_id}", tags=["MongoDB - Patients"])
async def update_patient_mongodb(patient_id: int, patient: PatientCreate):
    """Update patient in MongoDB Atlas"""
    if mongodb_db is None:
        raise HTTPException(status_code=500, detail="MongoDB not available")
    
    try:
        update_data = {
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "email": patient.email,
            "phone": patient.phone,
            "updated_at": datetime.now()
        }
        
        result = await mongodb_db.patients.update_one(
            {"patient_id": patient_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        return {"message": f"Patient {patient_id} updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating patient: {str(e)}")

@app.delete("/mongodb/patients/{patient_id}", tags=["MongoDB - Patients"])
async def delete_patient_mongodb(patient_id: int):
    """Delete patient from MongoDB Atlas"""
    if mongodb_db is None:
        raise HTTPException(status_code=500, detail="MongoDB not available")
    
    try:
        result = await mongodb_db.patients.delete_one({"patient_id": patient_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        return {"message": f"Patient {patient_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting patient: {str(e)}")

# ============================================================================
# MONGODB PREDICTION LOGS
# ============================================================================

@app.post("/mongodb/prediction-logs/", tags=["MongoDB - Prediction Logs"])
async def create_prediction_log(log_data: Dict[str, Any]):
    """Create a prediction log entry in MongoDB for audit trail"""
    if mongodb_db is None:
        raise HTTPException(status_code=500, detail="MongoDB not available")
    
    try:
        result = await mongodb_db.prediction_logs.insert_one(log_data)
        return {
            "message": "Prediction log created successfully",
            "log_id": str(result.inserted_id),
            "logged_at": log_data.get("prediction_date", "N/A")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating prediction log: {str(e)}")

@app.get("/mongodb/prediction-logs/", tags=["MongoDB - Prediction Logs"])
async def get_all_prediction_logs():
    """Get all prediction logs from MongoDB"""
    if mongodb_db is None:
        raise HTTPException(status_code=500, detail="MongoDB not available")
    
    try:
        logs = []
        async for log in mongodb_db.prediction_logs.find().sort("prediction_date", -1):
            log["_id"] = str(log["_id"])
            logs.append(log)
        return {"prediction_logs": logs, "count": len(logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching logs: {str(e)}")

@app.get("/mongodb/prediction-logs/{patient_id}", tags=["MongoDB - Prediction Logs"])
async def get_patient_prediction_logs(patient_id: int):
    """Get all prediction logs for a specific patient"""
    if mongodb_db is None:
        raise HTTPException(status_code=500, detail="MongoDB not available")
    
    try:
        logs = []
        async for log in mongodb_db.prediction_logs.find({"patient_id": patient_id}).sort("prediction_date", -1):
            log["_id"] = str(log["_id"])
            logs.append(log)
        
        if not logs:
            raise HTTPException(status_code=404, detail="No prediction logs found for this patient")
        
        return {"patient_id": patient_id, "prediction_logs": logs, "count": len(logs)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching logs: {str(e)}")

# ============================================================================
# MYSQL EXTENDED ENDPOINTS (Latest Patient, Medical History, Lab Results, Diagnoses)
# ============================================================================

@app.get("/mysql/patients/latest", response_model=PatientResponse, tags=["MySQL - Patients"])
def get_latest_patient_mysql(db: Session = Depends(get_mysql_db)):
    """Get the most recent patient from MySQL database"""
    patient = db.query(Patient).order_by(Patient.Patient_ID.desc()).first()
    if not patient:
        raise HTTPException(status_code=404, detail="No patients found")
    return patient

@app.get("/mysql/patients/latest/full-data", tags=["MySQL - Patients"])
def get_latest_patient_full_data(db: Session = Depends(get_mysql_db)):
    """
    Get the latest patient with all medical data (for prediction script)
    Returns: Patient info + Medical History + Lab Results
    """
    patient = db.query(Patient).order_by(Patient.Patient_ID.desc()).first()
    if not patient:
        raise HTTPException(status_code=404, detail="No patients found")
    
    # Get medical history
    medical_history = db.query(MedicalHistory).filter(
        MedicalHistory.Patient_ID == patient.Patient_ID
    ).first()
    
    # Get lab results
    lab_results = db.query(LabResults).filter(
        LabResults.Patient_ID == patient.Patient_ID
    ).first()
    
    if not medical_history or not lab_results:
        raise HTTPException(
            status_code=404, 
            detail="Complete medical data not found for latest patient"
        )
    
    return {
        "patient": {
            "Patient_ID": patient.Patient_ID,
            "Name": patient.Name,
            "Age": patient.Age,
            "Gender": patient.Gender,
            "Email": patient.Email,
            "Phone": patient.Phone
        },
        "medical_history": {
            "History_ID": medical_history.History_ID,
            "Patient_ID": medical_history.Patient_ID,
            "Diabetes": medical_history.Diabetes,
            "Hypertension": medical_history.Hypertension,
            "Record_Date": str(medical_history.Record_Date)
        },
        "lab_results": {
            "Lab_ID": lab_results.Lab_ID,
            "Patient_ID": lab_results.Patient_ID,
            "Creatinine_Level": float(lab_results.Creatinine_Level),
            "BUN_Level": float(lab_results.BUN_Level),
            "GFR_Value": float(lab_results.GFR_Value),
            "Urine_Output": float(lab_results.Urine_Output),
            "Test_Date": str(lab_results.Test_Date)
        }
    }

# Medical History Endpoints
@app.post("/mysql/medical-history/", tags=["MySQL - Medical History"])
def create_medical_history(patient_id: int, diabetes: bool, hypertension: bool, 
                          record_date: Optional[date] = None, 
                          db: Session = Depends(get_mysql_db)):
    """Create medical history record for a patient"""
    try:
        medical_history = MedicalHistory(
            Patient_ID=patient_id,
            Diabetes=diabetes,
            Hypertension=hypertension,
            Record_Date=record_date or date.today()
        )
        db.add(medical_history)
        db.commit()
        db.refresh(medical_history)
        return {"message": "Medical history created", "history_id": medical_history.History_ID}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating medical history: {str(e)}")

@app.get("/mysql/medical-history/{patient_id}", tags=["MySQL - Medical History"])
def get_medical_history(patient_id: int, db: Session = Depends(get_mysql_db)):
    """Get medical history for a patient"""
    history = db.query(MedicalHistory).filter(MedicalHistory.Patient_ID == patient_id).all()
    if not history:
        raise HTTPException(status_code=404, detail="No medical history found")
    return {"patient_id": patient_id, "records": history}

# Lab Results Endpoints
@app.post("/mysql/lab-results/", tags=["MySQL - Lab Results"])
def create_lab_results(patient_id: int, creatinine_level: float, bun_level: float,
                      gfr_value: float, urine_output: float, test_date: Optional[date] = None,
                      db: Session = Depends(get_mysql_db)):
    """Create lab results for a patient"""
    try:
        lab_result = LabResults(
            Patient_ID=patient_id,
            Creatinine_Level=creatinine_level,
            BUN_Level=bun_level,
            GFR_Value=gfr_value,
            Urine_Output=urine_output,
            Test_Date=test_date or date.today()
        )
        db.add(lab_result)
        db.commit()
        db.refresh(lab_result)
        return {"message": "Lab results created", "lab_id": lab_result.Lab_ID}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating lab results: {str(e)}")

@app.get("/mysql/lab-results/{patient_id}", tags=["MySQL - Lab Results"])
def get_lab_results(patient_id: int, db: Session = Depends(get_mysql_db)):
    """Get lab results for a patient"""
    results = db.query(LabResults).filter(LabResults.Patient_ID == patient_id).all()
    if not results:
        raise HTTPException(status_code=404, detail="No lab results found")
    return {"patient_id": patient_id, "results": results}

# Diagnosis Endpoints
@app.post("/mysql/diagnoses/", tags=["MySQL - Diagnoses"])
def create_diagnosis(patient_id: int, ckd_status: bool, risk_score: float,
                    diagnosed_by: str, diagnosis_date: Optional[date] = None,
                    model_version: Optional[str] = None,
                    db: Session = Depends(get_mysql_db)):
    """Create diagnosis record for a patient"""
    try:
        diagnosis = Diagnosis(
            Patient_ID=patient_id,
            CKD_Status=ckd_status,
            Risk_Score=risk_score,
            Diagnosed_By=diagnosed_by,
            Diagnosis_Date=diagnosis_date or date.today(),
            Model_Version=model_version or "Unknown"
        )
        db.add(diagnosis)
        db.commit()
        db.refresh(diagnosis)
        return {
            "message": "Diagnosis created successfully",
            "Diagnosis_ID": diagnosis.Diagnosis_ID,
            "Patient_ID": diagnosis.Patient_ID,
            "CKD_Status": diagnosis.CKD_Status,
            "Risk_Score": float(diagnosis.Risk_Score)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating diagnosis: {str(e)}")

@app.get("/mysql/diagnoses/{patient_id}", tags=["MySQL - Diagnoses"])
def get_diagnoses(patient_id: int, db: Session = Depends(get_mysql_db)):
    """Get all diagnoses for a patient"""
    diagnoses = db.query(Diagnosis).filter(Diagnosis.Patient_ID == patient_id).all()
    if not diagnoses:
        raise HTTPException(status_code=404, detail="No diagnoses found")
    return {"patient_id": patient_id, "diagnoses": diagnoses}

# ============================================================================
# ML PREDICTION ENDPOINTS
# ============================================================================

def make_prediction(patient_data: Dict) -> Dict:
    """Make ML prediction using loaded Random Forest model"""
    if ml_model is None:
        raise HTTPException(status_code=500, detail="ML model not available")
    
    try:
        # Prepare features in correct order
        features = [
            patient_data["Age"],
            patient_data["Creatinine_Level"],
            patient_data["BUN_Level"],
            patient_data["GFR_Value"],
            patient_data["Urine_Output"],
            1 if patient_data["Diabetes"] else 0,
            1 if patient_data["Hypertension"] else 0
        ]
        
        # Make prediction
        prediction = ml_model.predict([features])[0]
        probability = ml_model.predict_proba([features])[0]
        
        return {
            "prediction": "CKD" if prediction == 1 else "No CKD",
            "ckd_status": bool(prediction),
            "risk_score": float(probability[1]),
            "confidence": float(max(probability)),
            "prediction_date": datetime.now().isoformat(),
            "model_version": model_metadata.get("model_type", "RandomForest_v1.0") if model_metadata else "RandomForest_v1.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict/", response_model=MLPredictionResponse, tags=["ML Predictions"])
async def predict_kidney_disease(prediction_request: MLPredictionRequest):
    """Make kidney disease prediction with manual input"""
    try:
        patient_data = prediction_request.dict()
        result = make_prediction(patient_data)
        
        return MLPredictionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/predict-latest", tags=["Combined Tasks - Assignment Task 3"])
async def predict_latest_patient():
    """
    TASK 3 IMPLEMENTATION:
    1. Fetch latest patient data from MySQL
    2. Load ML model  
    3. Make prediction
    4. Log result to MongoDB
    5. Return prediction result
    """
    if mysql_engine is None:
        raise HTTPException(status_code=500, detail="MySQL database not available")
    if mongodb_db is None:
        raise HTTPException(status_code=500, detail="MongoDB database not available")
    if ml_model is None:
        raise HTTPException(status_code=500, detail="ML model not available")
    
    try:
        # Step 1: Fetch latest patient data from MySQL using stored procedure
        with mysql_engine.connect() as conn:
            # Get latest patient with complete data
            query = text("""
                SELECT p.Patient_ID, p.Age, 
                       lr.Creatinine_Level, lr.BUN_Level, lr.GFR_Value, lr.Urine_Output,
                       mh.Diabetes, mh.Hypertension
                FROM Patients p
                JOIN Lab_Results lr ON p.Patient_ID = lr.Patient_ID  
                JOIN Medical_History mh ON p.Patient_ID = mh.Patient_ID
                ORDER BY p.Patient_ID DESC
                LIMIT 1
            """)
            result = conn.execute(query)
            patient_data = result.fetchone()
            
            if not patient_data:
                raise HTTPException(status_code=404, detail="No patient data found")
            
            # Convert to dictionary
            patient_dict = {
                "Patient_ID": patient_data[0],
                "Age": patient_data[1],
                "Creatinine_Level": float(patient_data[2]),
                "BUN_Level": float(patient_data[3]),
                "GFR_Value": float(patient_data[4]),
                "Urine_Output": float(patient_data[5]),
                "Diabetes": bool(patient_data[6]),
                "Hypertension": bool(patient_data[7])
            }
        
        # Step 2 & 3: Load model and make prediction (already loaded)
        prediction_result = make_prediction(patient_dict)
        prediction_result["patient_id"] = patient_dict["Patient_ID"]
        
        # Step 4: Log prediction result to MongoDB
        log_entry = {
            "patient_id": patient_dict["Patient_ID"],
            "prediction": prediction_result["prediction"],
            "ckd_status": prediction_result["ckd_status"],
            "risk_score": prediction_result["risk_score"],
            "confidence": prediction_result["confidence"],
            "input_features": patient_dict,
            "model_version": prediction_result["model_version"],
            "prediction_date": prediction_result["prediction_date"],
            "source": "predict-latest endpoint",
            "assignment_task": "Task 3 - Fetch and Predict"
        }
        
        await mongodb_db.prediction_logs.insert_one(log_entry)
        
        # Step 5: Return complete result
        return {
            "status": "success",
            "message": "Latest patient data fetched, predicted, and logged successfully",
            "patient_data": patient_dict,
            "prediction_result": prediction_result,
            "logged_to_mongodb": True,
            "assignment_requirements": {
                "task_3_completed": True,
                "fetch_latest_data": "Completed",
                "load_model": "Completed", 
                "make_prediction": "Completed",
                "log_to_database": "Completed"
            }
        }
        
    except Exception as e:
        # Log error to MongoDB
        error_log = {
            "error": str(e),
            "endpoint": "/predict-latest",
            "timestamp": datetime.now().isoformat(),
            "error_type": "predict-latest-error"
        }
        if mongodb_db:
            await mongodb_db.error_logs.insert_one(error_log)
        
        raise HTTPException(status_code=500, detail=f"Prediction pipeline failed: {str(e)}")

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database tables and connections"""
    try:
        if mysql_engine:
            # Create tables if they don't exist
            Base.metadata.create_all(bind=mysql_engine)
            print("MySQL tables verified/created")
        
        if mongodb_client:
            # Test MongoDB connection
            await mongodb_client.admin.command('ping')
            print("MongoDB Atlas connection verified")
            
        print("Application startup completed successfully!")
        print("API Documentation: http://localhost:8000/docs")
        print("Health Check: http://localhost:8000/")
        
    except Exception as e:
        print(f"Startup warning: {e}")

if __name__ == "__main__":
    import uvicorn
    # Use environment variables for host and port configuration
    api_host = os.getenv("API_HOST", "0.0.0.0")
    api_port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host=api_host, port=api_port)