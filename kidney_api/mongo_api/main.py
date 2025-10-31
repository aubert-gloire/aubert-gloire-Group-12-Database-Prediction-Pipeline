import certifi
import motor.motor_asyncio
from fastapi import FastAPI, HTTPException, Body, status
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from bson import ObjectId
from typing import Optional, List
from pydantic import GetJsonSchemaHandler
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue

# --- 1. MongoDB Connection ---
MONGO_DETAILS = "mongodb+srv://hospital_db_user:hospital123@cluster0.8ef3cwc.mongodb.net/?appName=Cluster0"
client = motor.motor_asyncio.AsyncIOMotorClient(
    MONGO_DETAILS,
    tlsCAFile=certifi.where() 
) # Ensures proper SSL certificate verification
database = client.hospital_db
patient_collection = database.get_collection("patients")


# --- 2. Pydantic Models (API Schema) ---

# --- This is the FINAL Pydantic v2 code ---
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: object, handler: object
    ) -> core_schema.CoreSchema:
        """
        This method is used by Pydantic v2 to validate data.
        It ensures that the input is a valid ObjectId,
        and can convert a string to an ObjectId.
        """
        
        # This is the correct validator function
        from_string_validator = core_schema.no_info_plain_validator_function(cls.validate)
        
        return core_schema.union_schema(
            [
                # Check if it's already an ObjectId instance
                core_schema.is_instance_schema(ObjectId),
                
                # If not, try to validate it using our function
                from_string_validator,
            ],
            # This is the correct serialization function
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

    @classmethod
    def validate(cls, v: object) -> ObjectId:
        """Validate that the input is a valid ObjectId."""
        if isinstance(v, ObjectId):
            return v
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """
        This method is used by Pydantic v2 to generate the JSON schema
        (used by FastAPI for the /docs page).
        It tells the docs that this field expects a string.
        """
        return {"type": "string"}

# --- Models for Embedded Documents ---
class MedicalHistory(BaseModel):
    Diabetes: bool = False
    Hypertension: bool = False
    Record_Date: Optional[str] = None

class LabResult(BaseModel):
    Creatinine_Level: Optional[float] = None
    BUN_Level: Optional[float] = None
    GFR_Value: Optional[float] = None
    Urine_Output: Optional[float] = None
    Test_Date: Optional[str] = None

class Diagnosis(BaseModel):
    CKD_Status: bool
    Risk_Score: Optional[float] = None
    Diagnosed_By: Optional[str] = None
    Diagnosis_Date: Optional[str] = None
    Model_Version: Optional[str] = "RandomForest_v1.0"

# --- Base Patient Model (for POST, PUT) ---
class PatientBase(BaseModel):
    Name: str = Field(..., min_length=2)
    Age: int = Field(..., gt=0)
    Gender: Optional[str] = None
    Email: Optional[EmailStr] = None
    Phone: Optional[str] = None
    Medical_History: Optional[MedicalHistory] = None
    Lab_Results: List[LabResult] = []
    Diagnoses: List[Diagnosis] = []

    # --- THIS IS THE Pydantic v2 Config ---
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "Name": "John Doe",
                "Age": 45,
                "Gender": "Male",
                "Email": "john.doe@example.com",
                "Medical_History": {"Diabetes": True, "Hypertension": True},
                "Lab_Results": [
                    {"Creatinine_Level": 1.9, "BUN_Level": 25.0}
                ]
            }
        }
    )

# --- Patient Model for Responses (GET) ---
class PatientInDB(PatientBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    # --- THIS IS THE Pydantic v2 Config ---
    # We no longer need 'json_encoders' as PyObjectId handles serialization.
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

# --- 3. FastAPI App & Endpoints ---

app = FastAPI(title="Kidney Disease DB API (MongoDB)")


# --- CREATE (POST) ---
@app.post("/patients/", 
          response_description="Add new patient", 
          response_model=PatientInDB,
          status_code=status.HTTP_201_CREATED)
async def create_patient(patient: PatientBase = Body(...)):
    """
    Create a new patient document in the database.
    """
    # Use model_dump() instead of .dict() in Pydantic v2
    patient_dict = patient.model_dump() 
    new_patient = await patient_collection.insert_one(patient_dict)
    created_patient = await patient_collection.find_one({"_id": new_patient.inserted_id})
    return created_patient


# --- READ (GET All) ---
@app.get("/patients/", 
         response_description="List all patients", 
         response_model=List[PatientInDB])
async def list_patients(limit: int = 100):
    """
    Retrieve all patients from the database, with an optional limit.
    """
    patients = await patient_collection.find().to_list(limit)
    return patients


# --- READ (GET One by ID) ---
@app.get("/patients/{id}", 
         response_description="Get a single patient by ID", 
         response_model=PatientInDB)
async def get_patient(id: str):
    """
    Get a single patient by their unique MongoDB _id.
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"Invalid ID: {id}")
        
    patient = await patient_collection.find_one({"_id": ObjectId(id)})
    
    if patient is not None:
        return patient
    
    raise HTTPException(status_code=404, detail=f"Patient with ID {id} not found")


# --- UPDATE (PUT) ---
@app.put("/patients/{id}", 
         response_description="Update a patient's details", 
         response_model=PatientInDB)
async def update_patient(id: str, patient: PatientBase = Body(...)):
    """
    Update an existing patient's document by their ID.
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"Invalid ID: {id}")

    # Use model_dump() instead of .dict() in Pydantic v2
    update_data = patient.model_dump(exclude_unset=True) 
    
    if len(update_data) < 1:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await patient_collection.update_one(
        {"_id": ObjectId(id)}, {"$set": update_data}
    )

    if result.modified_count == 1:
        updated_patient = await patient_collection.find_one({"_id": ObjectId(id)})
        return updated_patient
    
    raise HTTPException(status_code=404, detail=f"Patient with ID {id} not found")


# --- DELETE (DELETE) ---
@app.delete("/patients/{id}", 
            response_description="Delete a patient", 
            status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(id: str):
    """
    Delete a patient document from the database by their ID.
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"Invalid ID: {id}")
        
    delete_result = await patient_collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return
    
    raise HTTPException(status_code=404, detail=f"Patient with ID {id} not found")