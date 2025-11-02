"""
Database Population Script for Kidney Disease Prediction System

This script populates both MySQL and MongoDB databases with comprehensive sample data
for testing and demonstration purposes.

Features:
- Creates realistic patient data with varied risk profiles
- Populates both relational (MySQL) and NoSQL (MongoDB) databases
- Includes patients with different CKD risk levels
- Generates medical history, lab results, and diagnosis records
- Uses environment variables for secure database connections

Usage:
    python populate_database.py

Requirements:
    - .env file with database credentials
    - MySQL database with schema already created
    - MongoDB Atlas cluster accessible
    - Required Python packages: pymysql, motor, pandas, asyncio
"""

import asyncio
import random
import pymysql
import motor.motor_asyncio
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
MYSQL_URL = os.getenv("MYSQL_URL")
MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "hospital_db")

class DatabasePopulator:
    def __init__(self):
        self.mysql_connection = None
        self.mongodb_client = None
        self.mongodb_db = None
        
    async def connect_databases(self):
        """Initialize connections to both databases"""
        try:
            # Parse MySQL URL
            if MYSQL_URL:
                # Extract connection details from URL
                # Format: mysql+pymysql://user:password@host:port/database
                url_parts = MYSQL_URL.replace("mysql+pymysql://", "").split("/")
                db_name = url_parts[1] if len(url_parts) > 1 else "kidney_disease_db"
                
                auth_host = url_parts[0].split("@")
                host_port = auth_host[1].split(":")
                user_pass = auth_host[0].split(":")
                
                self.mysql_connection = pymysql.connect(
                    host=host_port[0],
                    port=int(host_port[1]) if len(host_port) > 1 else 3306,
                    user=user_pass[0],
                    password=user_pass[1],
                    database=db_name,
                    charset='utf8mb4'
                )
                print(" MySQL connection established")
            else:
                print(" MySQL URL not found in environment variables")
                
            # Initialize MongoDB
            if MONGODB_URL:
                self.mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
                self.mongodb_db = self.mongodb_client[MONGODB_DATABASE]
                print(" MongoDB connection established")
            else:
                print(" MongoDB URL not found in environment variables")
                
        except Exception as e:
            print(f" Database connection error: {e}")
            raise
    
    def generate_sample_patients(self) -> List[Dict]:
        """Generate diverse patient data with varied risk profiles"""
        patients = [
            # High Risk Patients (Advanced CKD)
            {
                "name": "John Anderson",
                "age": 68,
                "gender": "Male",
                "email": "john.anderson@email.com",
                "phone": "+1-555-0101",
                "diabetes": True,
                "hypertension": True,
                "creatinine": 3.2,
                "bun": 52.5,
                "gfr": 22.8,
                "urine_output": 650.0,
                "risk_category": "Very High"
            },
            {
                "name": "Michael Johnson",
                "age": 71,
                "gender": "Male",
                "email": "michael.j@email.com",
                "phone": "+1-555-0104",
                "diabetes": False,
                "hypertension": True,
                "creatinine": 5.8,
                "bun": 78.9,
                "gfr": 12.3,
                "urine_output": 380.0,
                "risk_category": "Critical"
            },
            {
                "name": "Maria Garcia",
                "age": 59,
                "gender": "Female",
                "email": "maria.garcia@email.com",
                "phone": "+1-555-0105",
                "diabetes": True,
                "hypertension": True,
                "creatinine": 4.1,
                "bun": 64.2,
                "gfr": 18.7,
                "urine_output": 520.0,
                "risk_category": "Very High"
            },
            
            # Moderate Risk Patients
            {
                "name": "Sarah Martinez",
                "age": 52,
                "gender": "Female",
                "email": "sarah.martinez@email.com",
                "phone": "+1-555-0102",
                "diabetes": True,
                "hypertension": False,
                "creatinine": 1.8,
                "bun": 32.4,
                "gfr": 48.5,
                "urine_output": 950.0,
                "risk_category": "Moderate"
            },
            {
                "name": "Robert Wilson",
                "age": 64,
                "gender": "Male",
                "email": "robert.wilson@email.com",
                "phone": "+1-555-0107",
                "diabetes": False,
                "hypertension": True,
                "creatinine": 2.1,
                "bun": 38.7,
                "gfr": 42.3,
                "urine_output": 820.0,
                "risk_category": "Moderate-High"
            },
            {
                "name": "Linda Thompson",
                "age": 57,
                "gender": "Female",
                "email": "linda.thompson@email.com",
                "phone": "+1-555-0108",
                "diabetes": True,
                "hypertension": False,
                "creatinine": 1.6,
                "bun": 28.9,
                "gfr": 52.1,
                "urine_output": 1100.0,
                "risk_category": "Moderate"
            },
            
            # Low Risk Patients
            {
                "name": "Emily Chen",
                "age": 34,
                "gender": "Female",
                "email": "emily.chen@email.com",
                "phone": "+1-555-0103",
                "diabetes": False,
                "hypertension": False,
                "creatinine": 0.9,
                "bun": 14.2,
                "gfr": 98.5,
                "urine_output": 1500.0,
                "risk_category": "Low"
            },
            {
                "name": "David Kim",
                "age": 45,
                "gender": "Male",
                "email": "david.kim@email.com",
                "phone": "+1-555-0106",
                "diabetes": False,
                "hypertension": True,
                "creatinine": 1.2,
                "bun": 18.5,
                "gfr": 72.3,
                "urine_output": 1250.0,
                "risk_category": "Low-Moderate"
            },
            {
                "name": "Jennifer Brooks",
                "age": 29,
                "gender": "Female",
                "email": "jennifer.brooks@email.com",
                "phone": "+1-555-0109",
                "diabetes": False,
                "hypertension": False,
                "creatinine": 0.8,
                "bun": 12.1,
                "gfr": 110.2,
                "urine_output": 1650.0,
                "risk_category": "Very Low"
            },
            {
                "name": "Alex Rodriguez",
                "age": 38,
                "gender": "Other",
                "email": "alex.rodriguez@email.com",
                "phone": "+1-555-0110",
                "diabetes": False,
                "hypertension": False,
                "creatinine": 1.0,
                "bun": 15.8,
                "gfr": 89.4,
                "urine_output": 1420.0,
                "risk_category": "Low"
            }
        ]
        
        return patients
    
    def populate_mysql(self, patients: List[Dict]):
        """Populate MySQL database with patient data"""
        try:
            cursor = self.mysql_connection.cursor()
            
            # Clear existing data
            print("  Clearing existing MySQL data...")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            cursor.execute("TRUNCATE TABLE Diagnosis_Log")
            cursor.execute("TRUNCATE TABLE Diagnoses")
            cursor.execute("TRUNCATE TABLE Lab_Results")
            cursor.execute("TRUNCATE TABLE Medical_History")
            cursor.execute("TRUNCATE TABLE Patients")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            print(" Inserting patients into MySQL...")
            patient_ids = []
            
            for patient in patients:
                # Insert patient
                patient_query = """
                INSERT INTO Patients (Name, Age, Gender, Email, Phone) 
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(patient_query, (
                    patient['name'],
                    patient['age'],
                    patient['gender'],
                    patient['email'],
                    patient['phone']
                ))
                patient_id = cursor.lastrowid
                patient_ids.append(patient_id)
                
                # Insert medical history
                history_query = """
                INSERT INTO Medical_History (Patient_ID, Diabetes, Hypertension, Record_Date) 
                VALUES (%s, %s, %s, %s)
                """
                record_date = date.today() - timedelta(days=random.randint(1, 30))
                cursor.execute(history_query, (
                    patient_id,
                    patient['diabetes'],
                    patient['hypertension'],
                    record_date
                ))
                
                # Insert lab results
                lab_query = """
                INSERT INTO Lab_Results (Patient_ID, Creatinine_Level, BUN_Level, GFR_Value, Urine_Output, Test_Date) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                test_date = date.today() - timedelta(days=random.randint(0, 7))
                cursor.execute(lab_query, (
                    patient_id,
                    patient['creatinine'],
                    patient['bun'],
                    patient['gfr'],
                    patient['urine_output'],
                    test_date
                ))
                
                # Insert diagnosis for high-risk patients
                if patient['risk_category'] in ['Very High', 'Critical', 'Moderate-High']:
                    # Calculate risk score based on lab values
                    risk_score = self.calculate_risk_score(patient)
                    
                    diagnosis_query = """
                    INSERT INTO Diagnoses (Patient_ID, CKD_Status, Risk_Score, Diagnosed_By, Diagnosis_Date, Model_Version) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(diagnosis_query, (
                        patient_id,
                        True,  # CKD Status
                        risk_score,
                        'Dr. Database Populator',
                        date.today(),
                        'Initial_Assessment_v1.0'
                    ))
            
            self.mysql_connection.commit()
            print(f" Successfully inserted {len(patients)} patients into MySQL")
            return patient_ids
            
        except Exception as e:
            print(f" MySQL population error: {e}")
            self.mysql_connection.rollback()
            raise
        finally:
            cursor.close()
    
    async def populate_mongodb(self, patients: List[Dict], patient_ids: List[int]):
        """Populate MongoDB with patient data and prediction logs"""
        try:
            # Clear existing collections
            print("  Clearing existing MongoDB data...")
            await self.mongodb_db.patients.delete_many({})
            await self.mongodb_db.prediction_logs.delete_many({})
            
            print(" Inserting patients into MongoDB...")
            
            # Insert patients
            mongo_patients = []
            for i, patient in enumerate(patients):
                mongo_patient = {
                    "patient_id": patient_ids[i],
                    "name": patient['name'],
                    "age": patient['age'],
                    "gender": patient['gender'],
                    "email": patient['email'],
                    "phone": patient['phone'],
                    "medical_conditions": {
                        "diabetes": patient['diabetes'],
                        "hypertension": patient['hypertension']
                    },
                    "created_at": datetime.now(),
                    "source": "Database Population Script"
                }
                mongo_patients.append(mongo_patient)
            
            await self.mongodb_db.patients.insert_many(mongo_patients)
            
            # Insert prediction logs for patients with diagnoses
            print(" Inserting prediction logs into MongoDB...")
            prediction_logs = []
            
            for i, patient in enumerate(patients):
                if patient['risk_category'] in ['Very High', 'Critical', 'Moderate-High', 'Moderate']:
                    ckd_status = patient['risk_category'] in ['Very High', 'Critical', 'Moderate-High']
                    risk_score = self.calculate_risk_score(patient)
                    confidence = min(95, 70 + (risk_score * 25))  # High confidence for demo
                    
                    log_entry = {
                        "patient_id": patient_ids[i],
                        "prediction": "CKD" if ckd_status else "No CKD",
                        "ckd_status": ckd_status,
                        "risk_score": risk_score,
                        "confidence": confidence,
                        "input_features": {
                            "Age": patient['age'],
                            "Creatinine_Level": patient['creatinine'],
                            "BUN_Level": patient['bun'],
                            "GFR_Value": patient['gfr'],
                            "Urine_Output": patient['urine_output'],
                            "Diabetes": patient['diabetes'],
                            "Hypertension": patient['hypertension']
                        },
                        "model_version": "PopulationScript_v1.0",
                        "prediction_date": datetime.now(),
                        "source": "Database Population Script",
                        "risk_category": patient['risk_category']
                    }
                    prediction_logs.append(log_entry)
            
            if prediction_logs:
                await self.mongodb_db.prediction_logs.insert_many(prediction_logs)
            
            print(f" Successfully inserted {len(patients)} patients and {len(prediction_logs)} prediction logs into MongoDB")
            
        except Exception as e:
            print(f" MongoDB population error: {e}")
            raise
    
    def calculate_risk_score(self, patient: Dict) -> float:
        """Calculate risk score based on lab values and conditions"""
        risk_score = 0.0
        
        # GFR is most important (60% weight)
        if patient['gfr'] < 15:
            risk_score += 0.60
        elif patient['gfr'] < 30:
            risk_score += 0.50
        elif patient['gfr'] < 60:
            risk_score += 0.30
        else:
            risk_score += 0.05
        
        # BUN Level (23% weight)
        if patient['bun'] > 60:
            risk_score += 0.23
        elif patient['bun'] > 40:
            risk_score += 0.18
        elif patient['bun'] > 20:
            risk_score += 0.10
        else:
            risk_score += 0.02
        
        # Creatinine Level (13% weight)
        if patient['creatinine'] > 4.0:
            risk_score += 0.13
        elif patient['creatinine'] > 2.0:
            risk_score += 0.10
        elif patient['creatinine'] > 1.3:
            risk_score += 0.06
        else:
            risk_score += 0.01
        
        # Additional factors
        if patient['urine_output'] < 500:
            risk_score += 0.02
        if patient['diabetes']:
            risk_score += 0.01
        if patient['hypertension']:
            risk_score += 0.01
        
        return min(risk_score, 1.0)
    
    def generate_summary_report(self, patients: List[Dict]):
        """Generate a summary report of populated data"""
        print("\n" + "="*70)
        print(" DATABASE POPULATION SUMMARY REPORT")
        print("="*70)
        
        total_patients = len(patients)
        diabetes_count = sum(1 for p in patients if p['diabetes'])
        hypertension_count = sum(1 for p in patients if p['hypertension'])
        
        risk_categories = {}
        for patient in patients:
            category = patient['risk_category']
            risk_categories[category] = risk_categories.get(category, 0) + 1
        
        print(f" Total Patients: {total_patients}")
        print(f" Patients with Diabetes: {diabetes_count} ({diabetes_count/total_patients*100:.1f}%)")
        print(f" Patients with Hypertension: {hypertension_count} ({hypertension_count/total_patients*100:.1f}%)")
        
        print(f"\n Risk Distribution:")
        for category, count in risk_categories.items():
            print(f"   {category}: {count} patients ({count/total_patients*100:.1f}%)")
        
        print(f"\n Lab Value Ranges:")
        gfr_values = [p['gfr'] for p in patients]
        creatinine_values = [p['creatinine'] for p in patients]
        bun_values = [p['bun'] for p in patients]
        
        print(f"   GFR: {min(gfr_values):.1f} - {max(gfr_values):.1f} mL/min/1.73m²")
        print(f"   Creatinine: {min(creatinine_values):.1f} - {max(creatinine_values):.1f} mg/dL")
        print(f"   BUN: {min(bun_values):.1f} - {max(bun_values):.1f} mg/dL")
        
        print(f"\n Data successfully populated in both MySQL and MongoDB!")
        print("="*70)
    
    async def close_connections(self):
        """Close database connections"""
        if self.mysql_connection:
            self.mysql_connection.close()
            print("🔌 MySQL connection closed")
        
        if self.mongodb_client:
            self.mongodb_client.close()
            print("🔌 MongoDB connection closed")

async def main():
    """Main function to populate databases"""
    print(" Starting Database Population Script")
    print("="*50)
    
    # Check environment variables
    if not MYSQL_URL:
        print("   MYSQL_URL not found in environment variables")
        print("   Please check your .env file")
        return
    
    if not MONGODB_URL:
        print("   MONGODB_URL not found in environment variables")
        print("   Please check your .env file")
        return
    
    populator = DatabasePopulator()
    
    try:
        # Connect to databases
        await populator.connect_databases()
        
        # Generate sample data
        patients = populator.generate_sample_patients()
        print(f"  Generated {len(patients)} sample patients")
        
        # Populate MySQL
        patient_ids = populator.populate_mysql(patients)
        
        # Populate MongoDB
        await populator.populate_mongodb(patients, patient_ids)
        
        # Generate summary report
        populator.generate_summary_report(patients)
        
    except Exception as e:
        print(f"  Population failed: {e}")
    finally:
        await populator.close_connections()

if __name__ == "__main__":
    asyncio.run(main())