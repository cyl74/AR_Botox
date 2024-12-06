from datetime import date
from db import DatabaseAPI  

# Instantiate the Database API
db = DatabaseAPI()

# Add new patient
patient_id = db.add_patient("John Doe", "1234567890", "1990-01-01", "No known allergies")
print(f"Added patient with ID: {patient_id}")

# Get patient information
patient_info = db.get_patient(patient_id)
print(f"Patient info: {patient_info}")

# Update patient information
updated_patient = db.update_patient(patient_id, contact_info="0987654321")
print(f"Updated patient info: {updated_patient}")

# Remove patient
removed_patient = db.remove_patient(patient_id)
print(f"Removed patient: {removed_patient}")

# Get all patients
all_patients = db.get_all_patients()
print(f"All patients: {all_patients}")
