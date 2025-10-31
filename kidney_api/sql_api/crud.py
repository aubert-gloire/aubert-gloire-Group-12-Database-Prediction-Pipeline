from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models, schemas

# ---------------- Patients ----------------

def create_patient(db: Session, payload: schemas.PatientCreate):
    patient = models.Patient(**payload.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

def get_patients(db: Session):
    return db.query(models.Patient).all()

def get_patient(db: Session, patient_id: int):
    return db.query(models.Patient).filter(models.Patient.Patient_ID == patient_id).first()

def update_patient(db: Session, patient_id: int, payload: schemas.PatientCreate):
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    for key, value in payload.model_dump().items():
        setattr(patient, key, value)

    db.commit()
    db.refresh(patient)
    return patient

def delete_patient(db: Session, patient_id: int):
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    db.delete(patient)
    db.commit()
    return {"message": "Patient deleted"}


# ---------------- Medical History ----------------

def create_history(db: Session, payload: schemas.HistoryCreate):
    history = models.MedicalHistory(**payload.model_dump())
    db.add(history)
    db.commit()
    db.refresh(history)
    return history

def get_history(db: Session, patient_id: int):
    return db.query(models.MedicalHistory).filter(models.MedicalHistory.Patient_ID == patient_id).all()

# ---------------- Lab Results ----------------

def create_lab(db: Session, payload: schemas.LabCreate):
    lab = models.LabResult(**payload.model_dump())
    db.add(lab)
    db.commit()
    db.refresh(lab)
    return lab

def get_labs(db: Session, patient_id: int):
    return db.query(models.LabResult).filter(models.LabResult.Patient_ID == patient_id).all()

# ---------------- Diagnoses ----------------

def create_diagnosis(db: Session, payload: schemas.DiagnosisCreate):
    diag = models.Diagnosis(**payload.model_dump())
    db.add(diag)
    db.commit()
    db.refresh(diag)
    return diag

def get_diagnoses(db: Session):
    return db.query(models.Diagnosis).all()
