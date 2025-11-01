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

def update_history(db: Session, history_id: int, payload: schemas.HistoryCreate):
    history = db.query(models.MedicalHistory).filter(models.MedicalHistory.History_ID == history_id).first()
    if not history:
        raise HTTPException(404, "Medical history not found")

    for key, value in payload.model_dump().items():
        setattr(history, key, value)

    db.commit()
    db.refresh(history)
    return history

def delete_history(db: Session, history_id: int):
    history = db.query(models.MedicalHistory).filter(models.MedicalHistory.History_ID == history_id).first()
    if not history:
        raise HTTPException(404, "Medical history not found")

    db.delete(history)
    db.commit()
    return {"message": "Medical history deleted"}

# ---------------- Lab Results ----------------

def create_lab(db: Session, payload: schemas.LabCreate):
    lab = models.LabResult(**payload.model_dump())
    db.add(lab)
    db.commit()
    db.refresh(lab)
    return lab

def get_labs(db: Session, patient_id: int):
    return db.query(models.LabResult).filter(models.LabResult.Patient_ID == patient_id).all()

def update_lab(db: Session, lab_id: int, payload: schemas.LabCreate):
    lab = db.query(models.LabResult).filter(models.LabResult.Lab_ID == lab_id).first()
    if not lab:
        raise HTTPException(404, "Lab result not found")

    for key, value in payload.model_dump().items():
        setattr(lab, key, value)

    db.commit()
    db.refresh(lab)
    return lab

def delete_lab(db: Session, lab_id: int):
    lab = db.query(models.LabResult).filter(models.LabResult.Lab_ID == lab_id).first()
    if not lab:
        raise HTTPException(404, "Lab result not found")

    db.delete(lab)
    db.commit()
    return {"message": "Lab result deleted"}

# ---------------- Diagnoses ----------------

def create_diagnosis(db: Session, payload: schemas.DiagnosisCreate):
    diag = models.Diagnosis(**payload.model_dump())
    db.add(diag)
    db.commit()
    db.refresh(diag)
    return diag

def get_diagnoses(db: Session):
    return db.query(models.Diagnosis).all()

def get_diagnosis(db: Session, diagnosis_id: int):
    diagnosis = db.query(models.Diagnosis).filter(models.Diagnosis.Diagnosis_ID == diagnosis_id).first()
    if not diagnosis:
        raise HTTPException(404, "Diagnosis not found")
    return diagnosis

def update_diagnosis(db: Session, diagnosis_id: int, payload: schemas.DiagnosisCreate):
    diagnosis = db.query(models.Diagnosis).filter(models.Diagnosis.Diagnosis_ID == diagnosis_id).first()
    if not diagnosis:
        raise HTTPException(404, "Diagnosis not found")

    for key, value in payload.model_dump().items():
        setattr(diagnosis, key, value)

    db.commit()
    db.refresh(diagnosis)
    return diagnosis

def delete_diagnosis(db: Session, diagnosis_id: int):
    diagnosis = db.query(models.Diagnosis).filter(models.Diagnosis.Diagnosis_ID == diagnosis_id).first()
    if not diagnosis:
        raise HTTPException(404, "Diagnosis not found")

    db.delete(diagnosis)
    db.commit()
    return {"message": "Diagnosis deleted"}
