from sqlalchemy import Column, Integer, String, Boolean, Date, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Patient(Base):
    __tablename__ = "Patients"

    Patient_ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Name = Column(String(100))
    Age = Column(Integer, nullable=False)
    Gender = Column(String(20))
    Email = Column(String(255), unique=True)
    Phone = Column(String(20))

    history = relationship("MedicalHistory", back_populates="patient")
    labs = relationship("LabResult", back_populates="patient")
    diagnoses = relationship("Diagnosis", back_populates="patient")


class MedicalHistory(Base):
    __tablename__ = "Medical_History"

    History_ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Patient_ID = Column(Integer, ForeignKey("Patients.Patient_ID"))
    Diabetes = Column(Boolean, default=False)
    Hypertension = Column(Boolean, default=False)
    Record_Date = Column(Date)

    patient = relationship("Patient", back_populates="history")


class LabResult(Base):
    __tablename__ = "Lab_Results"

    Lab_ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Patient_ID = Column(Integer, ForeignKey("Patients.Patient_ID"))
    Creatinine_Level = Column(DECIMAL(5,2))
    BUN_Level = Column(DECIMAL(5,2))
    GFR_Value = Column(DECIMAL(5,2))
    Urine_Output = Column(DECIMAL(6,2))
    Test_Date = Column(Date)

    patient = relationship("Patient", back_populates="labs")


class Diagnosis(Base):
    __tablename__ = "Diagnoses"

    Diagnosis_ID = Column(Integer, primary_key=True, autoincrement=True)
    Patient_ID = Column(Integer, ForeignKey("Patients.Patient_ID"))
    CKD_Status = Column(Boolean, nullable=False)
    Risk_Score = Column(DECIMAL(5,4))
    Diagnosed_By = Column(String(100))
    Diagnosis_Date = Column(Date)
    Model_Version = Column(String(50))

    patient = relationship("Patient", back_populates="diagnoses")


class Diagnosis_Log(Base):
    __tablename__ = "Diagnosis_Log"

    Log_ID = Column(Integer, primary_key=True, autoincrement=True)
    Patient_ID = Column(Integer)
    CKD_Status = Column(Boolean)
    Risk_Score = Column(DECIMAL(5,4))
    Log_Date = Column(Date)
