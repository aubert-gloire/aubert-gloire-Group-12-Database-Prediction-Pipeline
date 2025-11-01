from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models, schemas, crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kidney Disease SQL API (Aiven Cloud)")


# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =============== Patients ===============

@app.post("/patients", response_model=schemas.Patient)
def create_patient(payload: schemas.PatientCreate, db: Session = Depends(get_db)):
    return crud.create_patient(db, payload)

@app.get("/patients", response_model=list[schemas.Patient])
def list_patients(db: Session = Depends(get_db)):
    return crud.get_patients(db)

@app.get("/patients/latest", response_model=schemas.Patient)
def get_latest_patient(db: Session = Depends(get_db)):
    return db.query(models.Patient).order_by(models.Patient.Patient_ID.desc()).first()

@app.get("/patients/{patient_id}", response_model=schemas.Patient)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    return crud.get_patient(db, patient_id)

@app.put("/patients/{patient_id}", response_model=schemas.Patient)
def edit_patient(patient_id: int, payload: schemas.PatientCreate, db: Session = Depends(get_db)):
    return crud.update_patient(db, patient_id, payload)

@app.delete("/patients/{patient_id}")
def remove_patient(patient_id: int, db: Session = Depends(get_db)):
    return crud.delete_patient(db, patient_id)


# =============== Medical History ===============

@app.post("/history", response_model=schemas.MedicalHistory)
def create_history(payload: schemas.HistoryCreate, db: Session = Depends(get_db)):
    return crud.create_history(db, payload)

@app.get("/history/{patient_id}", response_model=list[schemas.MedicalHistory])
def read_history(patient_id: int, db: Session = Depends(get_db)):
    return crud.get_history(db, patient_id)

@app.put("/history/{history_id}", response_model=schemas.MedicalHistory)
def update_history(history_id: int, payload: schemas.HistoryCreate, db: Session = Depends(get_db)):
    return crud.update_history(db, history_id, payload)

@app.delete("/history/{history_id}")
def delete_history(history_id: int, db: Session = Depends(get_db)):
    return crud.delete_history(db, history_id)


# =============== Lab Results ===============

@app.post("/labs", response_model=schemas.LabResult)
def create_lab(payload: schemas.LabCreate, db: Session = Depends(get_db)):
    return crud.create_lab(db, payload)

@app.get("/labs/{patient_id}", response_model=list[schemas.LabResult])
def read_labs(patient_id: int, db: Session = Depends(get_db)):
    return crud.get_labs(db, patient_id)

@app.put("/labs/{lab_id}", response_model=schemas.LabResult)
def update_lab(lab_id: int, payload: schemas.LabCreate, db: Session = Depends(get_db)):
    return crud.update_lab(db, lab_id, payload)

@app.delete("/labs/{lab_id}")
def delete_lab(lab_id: int, db: Session = Depends(get_db)):
    return crud.delete_lab(db, lab_id)


# =============== Diagnoses ===============

@app.post("/diagnoses", response_model=schemas.Diagnosis)
def create_diagnosis(payload: schemas.DiagnosisCreate, db: Session = Depends(get_db)):
    return crud.create_diagnosis(db, payload)

@app.get("/diagnoses", response_model=list[schemas.Diagnosis])
def read_diagnoses(db: Session = Depends(get_db)):
    return crud.get_diagnoses(db)

@app.get("/diagnoses/{diagnosis_id}", response_model=schemas.Diagnosis)
def read_diagnosis(diagnosis_id: int, db: Session = Depends(get_db)):
    return crud.get_diagnosis(db, diagnosis_id)

@app.put("/diagnoses/{diagnosis_id}", response_model=schemas.Diagnosis)
def update_diagnosis(diagnosis_id: int, payload: schemas.DiagnosisCreate, db: Session = Depends(get_db)):
    return crud.update_diagnosis(db, diagnosis_id, payload)

@app.delete("/diagnoses/{diagnosis_id}")
def delete_diagnosis(diagnosis_id: int, db: Session = Depends(get_db)):
    return crud.delete_diagnosis(db, diagnosis_id)
