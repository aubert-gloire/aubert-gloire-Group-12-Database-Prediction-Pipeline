# Group12_Kidney-Disease-Prediction
Kidney Disease Risk Prediction System with Database Integration

## Project Overview
This project addresses the design and implementation of a database system and API integration to support predictive analytics on kidney disease risk assessment. Utilizing a comprehensive kidney disease dataset, the team developed both relational (SQL) and NoSQL (MongoDB) databases, implemented FastAPI CRUD endpoints, and created a script for fetching, preprocessing data, and making machine learning predictions.

The goal is to provide accurate kidney disease risk predictions to aid early intervention and clinical decision-making.

## Quick Start Guide

### Prerequisites

- Python 3.8 or higher
- MySQL database access
- MongoDB Atlas account

### Installation and Setup

1. **Clone and Install Dependencies**

   ```bash
   git clone <repository-url>
   cd aubert-gloire-Group-12-Database-Prediction-Pipeline
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**

   ```bash
   # Copy the environment template
   cp .env.example .env
   
   # Edit .env file with your actual database credentials
   # Required variables:
   # - MYSQL_URL (your MySQL connection string)
   # - MONGODB_URL (your MongoDB Atlas connection string)
   # - MONGODB_DATABASE (database name, default: hospital_db)
   ```

3. **Set Up Database Schema and Sample Data**

   ```bash
   # Create the database schema (run SQL script in your MySQL server)
   mysql -u username -p < database_schema.sql
   
   # Populate with sample data (automated script)
   python populate_database.py
   
   # Or use the comprehensive setup script
   python setup_database.py
   ```

4. **Run the Application**

   ```bash
   # Start the API server
   python kidney_disease_api.py
   ```

5. **Alternative Usage Options**

   **Option A: Use the Web Interface**
   ```bash
   # After starting the API, open the web interface
   # Navigate to frontend/index.html in your browser
   # Or serve it locally:
   cd frontend
   python -m http.server 8080
   # Then visit: http://localhost:8080
   ```

   **Option B: Run Standalone Prediction Script**
   ```bash
   # Make a prediction on the latest patient data
   python predict_latest_patient.py
   ```

### Accessing the Application

**API Server:**
- API Server: <http://localhost:8000>
- Interactive Documentation: <http://localhost:8000/docs>
- Health Check: <http://localhost:8000/>

**Web Interface:**
- Frontend: <http://localhost:8080> (if serving frontend locally)
- Direct access: Open `frontend/index.html` in your browser

**Standalone Script:**
- Run `python predict_latest_patient.py` for command-line predictions

### Available Endpoints

#### Health Check
- `GET /` - Application health check and system status

#### MySQL - Patient Management
- `POST /mysql/patients/` - Create new patient
- `GET /mysql/patients/` - Get all patients
- `GET /mysql/patients/{patient_id}` - Get specific patient by ID
- `PUT /mysql/patients/{patient_id}` - Update patient information
- `DELETE /mysql/patients/{patient_id}` - Delete patient
- `GET /mysql/patients/latest` - Get the most recent patient
- `GET /mysql/patients/latest/full-data` - Get latest patient with complete medical data

#### MySQL - Medical History
- `POST /mysql/medical-history/` - Create medical history record
- `GET /mysql/medical-history/{patient_id}` - Get medical history for patient

#### MySQL - Lab Results
- `POST /mysql/lab-results/` - Create lab results record
- `GET /mysql/lab-results/{patient_id}` - Get lab results for patient

#### MySQL - Diagnoses
- `POST /mysql/diagnoses/` - Create diagnosis record
- `GET /mysql/diagnoses/{patient_id}` - Get all diagnoses for patient

#### MongoDB - Patient Management
- `POST /mongodb/patients/` - Create new patient in MongoDB
- `GET /mongodb/patients/` - Get all patients from MongoDB
- `GET /mongodb/patients/{patient_id}` - Get specific patient from MongoDB
- `PUT /mongodb/patients/{patient_id}` - Update patient in MongoDB
- `DELETE /mongodb/patients/{patient_id}` - Delete patient from MongoDB

#### MongoDB - Prediction Logs
- `POST /mongodb/prediction-logs/` - Create prediction log entry
- `GET /mongodb/prediction-logs/` - Get all prediction logs
- `GET /mongodb/prediction-logs/{patient_id}` - Get prediction logs for specific patient

#### Machine Learning Predictions
- `POST /predict/` - Make kidney disease prediction with manual input
- `GET /predict-latest` - Fetch latest patient data and make prediction (Assignment Task 3)

## Project Structure

```text
├── kidney_disease_api.py          # Main API application
├── predict_latest_patient.py      # Standalone prediction script
├── populate_database.py           # Database population script (NEW)
├── setup_database.py              # Automated setup script (NEW)
├── setup_database.bat             # Windows setup batch file (NEW)
├── models/                        # Pre-trained ML model files
├── frontend/                      # Web interface files
├── .env.example                   # Environment variables template
├── database_schema.sql            # MySQL database schema
├── sample_data.sql               # Sample data for testing (SQL format)
└── requirements.txt              # Python dependencies
```

## Database Population

### Automated Population Script

The project includes a comprehensive Python script to populate both MySQL and MongoDB databases with realistic sample data:

**Key Features:**
- 🎯 **Diverse Risk Profiles**: Generates patients with varied CKD risk levels (Low, Moderate, High, Critical)
- 🏥 **Realistic Medical Data**: Includes proper lab values, medical histories, and demographic information
- 💾 **Dual Database Support**: Populates both MySQL (relational) and MongoDB (NoSQL) simultaneously
- 📊 **Comprehensive Coverage**: Creates 10 patients with complete medical profiles
- 🔄 **Automatic Cleanup**: Safely clears existing data before population

**Usage Options:**

1. **Automated Setup (Recommended):**
   ```bash
   # Complete setup including dependencies and population
   python setup_database.py
   
   # Windows users can also use:
   setup_database.bat
   ```

2. **Manual Population Only:**
   ```bash
   # If schema already exists, just populate data
   python populate_database.py
   ```

3. **SQL Script (Alternative):**
   ```bash
   # Traditional SQL approach
   mysql -u username -p < sample_data.sql
   ```

**Sample Data Includes:**
- **High Risk Patients**: Advanced CKD cases with low GFR, high creatinine
- **Moderate Risk Patients**: Stage 3 CKD with controlled comorbidities  
- **Low Risk Patients**: Normal kidney function, young and healthy profiles
- **Complete Lab Results**: Creatinine, BUN, GFR, Urine Output values
- **Medical History**: Diabetes and hypertension status
- **Prediction Logs**: Historical ML predictions for testing

## Features and Deliverables

### Database Design and Implementation

- Developed a relational database schema with four tables (Patients, Medical_History, Lab_Results, Diagnoses), including primary and foreign keys.
- Created an Entity-Relationship Diagram (ERD) to illustrate database relationships.
- Implemented the schema in MongoDB collections to support NoSQL storage with aggregation pipelines.
- Developed stored procedures and triggers in the relational database to automate validation and logging.

### API Endpoints

- Implemented FastAPI endpoints supporting full CRUD operations on both MySQL and MongoDB databases.
- Input validation and error handling with Pydantic models to ensure robust and secure API interactions.
- Integrated Swagger UI documentation for interactive API testing.
- Advanced endpoints for stored procedures and MongoDB aggregation pipelines.

### Machine Learning Pipeline
- Developed a RandomForestClassifier model to predict kidney disease status with 100% accuracy.
- Created a comprehensive prediction script that:
  - Fetches the latest patient data via the API.
  - Preprocesses and prepares the data for prediction.
  - Loads the trained model and generates predictions.
  - Logs prediction results back into both databases.
- Integrated `/predict-latest` endpoint combining all assignment tasks.

## Dataset
- **Dataset**: Kidney Disease Risk Dataset
- **Records**: 2,304 patient records
- **Features**: 9 clinical features including Age, Creatinine Level, BUN, GFR, Urine Output, Diabetes, and Hypertension
- **Target**: Binary classification (CKD Status prediction)
- **Source**: <https://www.kaggle.com/datasets/miadul/kidney-disease-risk-dataset>

## Technology Stack
- **Backend**: FastAPI, Python 3.12
- **Databases**: MySQL (Relational), MongoDB Atlas (NoSQL)
- **Machine Learning**: scikit-learn, Random Forest Classifier
- **Data Processing**: pandas, numpy
- **API Documentation**: Swagger UI, ReDoc
- **Database Drivers**: SQLAlchemy, PyMySQL, Motor (AsyncIO MongoDB)
