from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import date
from typing import Optional

# ----------- Patients -----------

class PatientBase(BaseModel):
    Name: str
    Age: int
    Gender: str
    Email: EmailStr
    Phone: str

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    Patient_ID: int

    model_config = ConfigDict(from_attributes=True)

# ----------- Medical History -----------

class HistoryBase(BaseModel):
    Patient_ID: int
    Diabetes: bool
    Hypertension: bool
    Record_Date: Optional[date] = None

class HistoryCreate(HistoryBase):
    pass

class MedicalHistory(HistoryBase):
    History_ID: int

    model_config = ConfigDict(from_attributes=True)
# ----------- Lab Results -----------

class LabBase(BaseModel):
    Patient_ID: int
    Creatinine_Level: float
    BUN_Level: float
    GFR_Value: float
    Urine_Output: float
    Test_Date: Optional[date] = None

class LabCreate(LabBase):
    pass

class LabResult(LabBase):
    Lab_ID: int

    model_config = ConfigDict(from_attributes=True)


# ----------- Diagnoses -----------

class DiagnosisBase(BaseModel):
    Patient_ID: int
    CKD_Status: bool
    Risk_Score: float
    Diagnosed_By: str
    Model_Version: Optional[str] = "RandomForest_v1.0"

class DiagnosisCreate(DiagnosisBase):
    pass

class Diagnosis(DiagnosisBase):
    Diagnosis_ID: int

    model_config = ConfigDict(from_attributes=True)
