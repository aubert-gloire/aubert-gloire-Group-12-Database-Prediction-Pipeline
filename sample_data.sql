-- ============================================
-- Sample Patient Data for Kidney Disease Prediction System
-- ============================================
-- This file inserts test data into the database for testing predictions
-- Run this AFTER creating the schema with database_schema.sql

USE kidney_disease_db;

-- Clear existing data (if any)
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE Diagnosis_Log;
TRUNCATE TABLE Diagnoses;
TRUNCATE TABLE Lab_Results;
TRUNCATE TABLE Medical_History;
TRUNCATE TABLE Patients;
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- Insert Patients
-- ============================================

-- Patient 1: High Risk CKD Patient (Elderly with complications)
INSERT INTO Patients (Name, Age, Gender, Email, Phone) VALUES
('John Anderson', 68, 'Male', 'john.anderson@email.com', '+1-555-0101');

-- Patient 2: Moderate Risk Patient (Middle-aged with diabetes)
INSERT INTO Patients (Name, Age, Gender, Email, Phone) VALUES
('Sarah Martinez', 52, 'Female', 'sarah.martinez@email.com', '+1-555-0102');

-- Patient 3: Low Risk Patient (Young and healthy)
INSERT INTO Patients (Name, Age, Gender, Email, Phone) VALUES
('Emily Chen', 34, 'Female', 'emily.chen@email.com', '+1-555-0103');

-- Patient 4: High Risk Patient (Severe kidney impairment)
INSERT INTO Patients (Name, Age, Gender, Email, Phone) VALUES
('Michael Johnson', 71, 'Male', 'michael.j@email.com', '+1-555-0104');

-- Patient 5: Moderate-High Risk Patient (Pre-dialysis)
INSERT INTO Patients (Name, Age, Gender, Email, Phone) VALUES
('Maria Garcia', 59, 'Female', 'maria.garcia@email.com', '+1-555-0105');

-- Patient 6: Low Risk Patient (Athletic, well-controlled conditions)
INSERT INTO Patients (Name, Age, Gender, Email, Phone) VALUES
('David Kim', 45, 'Male', 'david.kim@email.com', '+1-555-0106');

-- ============================================
-- Insert Medical History
-- ============================================

-- Patient 1: Has both diabetes and hypertension
INSERT INTO Medical_History (Patient_ID, Diabetes, Hypertension, Record_Date) VALUES
(1, TRUE, TRUE, '2025-01-15');

-- Patient 2: Has diabetes only
INSERT INTO Medical_History (Patient_ID, Diabetes, Hypertension, Record_Date) VALUES
(2, TRUE, FALSE, '2025-02-10');

-- Patient 3: No comorbidities
INSERT INTO Medical_History (Patient_ID, Diabetes, Hypertension, Record_Date) VALUES
(3, FALSE, FALSE, '2025-03-05');

-- Patient 4: Has hypertension only
INSERT INTO Medical_History (Patient_ID, Diabetes, Hypertension, Record_Date) VALUES
(4, FALSE, TRUE, '2025-01-20');

-- Patient 5: Has both conditions
INSERT INTO Medical_History (Patient_ID, Diabetes, Hypertension, Record_Date) VALUES
(5, TRUE, TRUE, '2025-02-28');

-- Patient 6: Has hypertension (well controlled)
INSERT INTO Medical_History (Patient_ID, Diabetes, Hypertension, Record_Date) VALUES
(6, FALSE, TRUE, '2025-03-15');

-- ============================================
-- Insert Lab Results
-- ============================================

-- Patient 1: High Risk Labs (Advanced CKD - Stage 4)
-- Low GFR, High Creatinine, High BUN, Low Urine Output
INSERT INTO Lab_Results (Patient_ID, Creatinine_Level, BUN_Level, GFR_Value, Urine_Output, Test_Date) VALUES
(1, 3.2, 52.5, 22.8, 650.0, '2025-10-28');

-- Patient 2: Moderate Risk Labs (Stage 3 CKD)
-- Moderately reduced GFR, Elevated Creatinine
INSERT INTO Lab_Results (Patient_ID, Creatinine_Level, BUN_Level, GFR_Value, Urine_Output, Test_Date) VALUES
(2, 1.8, 32.4, 48.5, 950.0, '2025-10-29');

-- Patient 3: Low Risk Labs (Normal kidney function)
-- Normal values across the board
INSERT INTO Lab_Results (Patient_ID, Creatinine_Level, BUN_Level, GFR_Value, Urine_Output, Test_Date) VALUES
(3, 0.9, 14.2, 98.5, 1500.0, '2025-10-30');

-- Patient 4: Very High Risk Labs (Stage 5 CKD - Pre-dialysis)
-- Very low GFR, Very high Creatinine and BUN
INSERT INTO Lab_Results (Patient_ID, Creatinine_Level, BUN_Level, GFR_Value, Urine_Output, Test_Date) VALUES
(4, 5.8, 78.9, 12.3, 380.0, '2025-10-27');

-- Patient 5: High Risk Labs (Borderline Stage 4-5)
-- Low GFR approaching dialysis threshold
INSERT INTO Lab_Results (Patient_ID, Creatinine_Level, BUN_Level, GFR_Value, Urine_Output, Test_Date) VALUES
(5, 4.1, 64.2, 18.7, 520.0, '2025-10-31');

-- Patient 6: Low-Moderate Risk Labs (Early Stage 2 CKD)
-- Mildly reduced GFR but otherwise normal
INSERT INTO Lab_Results (Patient_ID, Creatinine_Level, BUN_Level, GFR_Value, Urine_Output, Test_Date) VALUES
(6, 1.2, 18.5, 72.3, 1250.0, '2025-11-01');

-- ============================================
-- Insert Sample Diagnoses (Optional - for testing)
-- ============================================

-- Add a few historical diagnoses to show the system works
-- These will also populate the Diagnosis_Log via trigger

INSERT INTO Diagnoses (Patient_ID, CKD_Status, Risk_Score, Diagnosed_By, Diagnosis_Date, Model_Version) VALUES
(1, TRUE, 0.9876, 'Dr. Smith (Manual)', '2025-10-28', 'Clinical_Assessment');

INSERT INTO Diagnoses (Patient_ID, CKD_Status, Risk_Score, Diagnosed_By, Diagnosis_Date, Model_Version) VALUES
(4, TRUE, 0.9954, 'Dr. Johnson (Manual)', '2025-10-27', 'Clinical_Assessment');

INSERT INTO Diagnoses (Patient_ID, CKD_Status, Risk_Score, Diagnosed_By, Diagnosis_Date, Model_Version) VALUES
(3, FALSE, 0.0523, 'Dr. Lee (Manual)', '2025-10-30', 'Clinical_Assessment');

-- ============================================
-- Verification Queries
-- ============================================

-- Display all patients with their complete data
SELECT
    p.Patient_ID,
    p.Name,
    p.Age,
    p.Gender,
    mh.Diabetes,
    mh.Hypertension,
    lr.Creatinine_Level,
    lr.BUN_Level,
    lr.GFR_Value,
    lr.Urine_Output,
    lr.Test_Date
FROM Patients p
LEFT JOIN Medical_History mh ON p.Patient_ID = mh.Patient_ID
LEFT JOIN Lab_Results lr ON p.Patient_ID = lr.Patient_ID
ORDER BY p.Patient_ID;

-- Show existing diagnoses
SELECT
    d.Diagnosis_ID,
    p.Name,
    d.CKD_Status,
    d.Risk_Score,
    d.Diagnosed_By,
    d.Diagnosis_Date
FROM Diagnoses d
JOIN Patients p ON d.Patient_ID = p.Patient_ID
ORDER BY d.Diagnosis_Date DESC;

-- Show the latest patient (this is what the prediction script will fetch)
SELECT
    p.Patient_ID,
    p.Name,
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
ORDER BY p.Patient_ID DESC
LIMIT 1;

-- ============================================
-- Summary Statistics
-- ============================================
SELECT
    COUNT(*) as Total_Patients,
    SUM(CASE WHEN mh.Diabetes = TRUE THEN 1 ELSE 0 END) as Patients_With_Diabetes,
    SUM(CASE WHEN mh.Hypertension = TRUE THEN 1 ELSE 0 END) as Patients_With_Hypertension,
    AVG(lr.GFR_Value) as Avg_GFR,
    AVG(lr.Creatinine_Level) as Avg_Creatinine
FROM Patients p
JOIN Medical_History mh ON p.Patient_ID = mh.Patient_ID
JOIN Lab_Results lr ON p.Patient_ID = lr.Patient_ID;

-- ============================================
-- Expected Prediction Results (for reference)
-- ============================================
/*
Based on the model's feature importance (GFR: 60%, BUN: 23%, Creatinine: 13%):

Patient 1 (John Anderson):
  - GFR: 22.8 (Very Low) + High Creatinine (3.2) + High BUN (52.5)
  - Expected: CKD POSITIVE (High Risk ~95-99%)

Patient 2 (Sarah Martinez):
  - GFR: 48.5 (Low) + Moderate Creatinine (1.8) + Moderate BUN (32.4)
  - Expected: CKD POSITIVE (Moderate-High Risk ~70-85%)

Patient 3 (Emily Chen):
  - GFR: 98.5 (Normal) + Normal Creatinine (0.9) + Normal BUN (14.2)
  - Expected: CKD NEGATIVE (Low Risk ~5-10%)

Patient 4 (Michael Johnson):
  - GFR: 12.3 (Critical) + Very High Creatinine (5.8) + Very High BUN (78.9)
  - Expected: CKD POSITIVE (Very High Risk ~99%)

Patient 5 (Maria Garcia):
  - GFR: 18.7 (Very Low) + High Creatinine (4.1) + High BUN (64.2)
  - Expected: CKD POSITIVE (Very High Risk ~95-99%)

Patient 6 (David Kim):
  - GFR: 72.3 (Mildly Low) + Normal Creatinine (1.2) + Normal BUN (18.5)
  - Expected: CKD NEGATIVE or BORDERLINE (Low-Moderate Risk ~30-50%)
*/

-- ============================================
-- Data Insertion Complete
-- ============================================
SELECT 'Sample data inserted successfully!' as Status;
