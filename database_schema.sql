-- Create database
CREATE DATABASE IF NOT EXISTS kidney_disease_db;
USE kidney_disease_db;

-- TABLE 1: PATIENTS (Demographics)
CREATE TABLE Patients (
    Patient_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100),
    Age INT NOT NULL,
    Gender ENUM('Male', 'Female', 'Other'),
    Email VARCHAR(255) UNIQUE,
    Phone VARCHAR(20)
);

-- TABLE 2: MEDICAL_HISTORY (Patient conditions)
CREATE TABLE Medical_History (
    History_ID INT AUTO_INCREMENT PRIMARY KEY,
    Patient_ID INT,
    Diabetes BOOLEAN DEFAULT FALSE,
    Hypertension BOOLEAN DEFAULT FALSE,
    Record_Date DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (Patient_ID) REFERENCES Patients(Patient_ID) ON DELETE CASCADE
);

-- TABLE 3: LAB_RESULTS (Laboratory test results)
CREATE TABLE Lab_Results (
    Lab_ID INT AUTO_INCREMENT PRIMARY KEY,
    Patient_ID INT,
    Creatinine_Level DECIMAL(5,2),
    BUN_Level DECIMAL(5,2),
    GFR_Value DECIMAL(5,2),
    Urine_Output DECIMAL(6,2),
    Test_Date DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (Patient_ID) REFERENCES Patients(Patient_ID) ON DELETE CASCADE
);

-- TABLE 4: DIAGNOSES (ML Model predictions and results)
CREATE TABLE Diagnoses (
    Diagnosis_ID INT AUTO_INCREMENT PRIMARY KEY,
    Patient_ID INT,
    CKD_Status BOOLEAN NOT NULL,
    Risk_Score DECIMAL(5,4),
    Diagnosed_By VARCHAR(100),
    Diagnosis_Date DATE DEFAULT (CURRENT_DATE),
    Model_Version VARCHAR(50) DEFAULT 'RandomForest_v1.0',
    FOREIGN KEY (Patient_ID) REFERENCES Patients(Patient_ID) ON DELETE CASCADE
);

-- STORED PROCEDURE: Get Patient Data for ML Prediction
DELIMITER //

CREATE PROCEDURE GetPatientData(
    IN p_patient_id INT
)
BEGIN
    SELECT 
        p.Patient_ID,
        p.Age,
        lr.Creatinine_Level,
        lr.BUN_Level,
        lr.GFR_Value,
        lr.Urine_Output,
        mh.Diabetes,
        mh.Hypertension
    FROM Patients p
    JOIN Medical_History mh ON p.Patient_ID = mh.Patient_ID
    JOIN Lab_Results lr ON p.Patient_ID = lr.Patient_ID
    WHERE p.Patient_ID = p_patient_id;
END //

DELIMITER ;

-- TRIGGER: Log Diagnosis Changes
DELIMITER //

CREATE TRIGGER log_diagnosis_changes
AFTER INSERT ON Diagnoses
FOR EACH ROW
BEGIN
    INSERT INTO Diagnosis_Log(Patient_ID, CKD_Status, Risk_Score, Log_Date)
    VALUES (NEW.Patient_ID, NEW.CKD_Status, NEW.Risk_Score, NOW());
END //

DELIMITER ;

-- DIAGNOSIS_LOG (For trigger)
CREATE TABLE Diagnosis_Log (
    Log_ID INT AUTO_INCREMENT PRIMARY KEY,
    Patient_ID INT,
    CKD_Status BOOLEAN,
    Risk_Score DECIMAL(5,4),
    Log_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

