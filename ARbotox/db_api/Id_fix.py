from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.orm import sessionmaker, relationship, joinedload, declarative_base
from datetime import datetime, date
import json
import pandas as pd

# Database connection details for MySQL
DB_USERNAME = 'root'                  # Replace with your MySQL username
DB_PASSWORD = 'password'                     # Replace with your MySQL password
DB_HOST = 'localhost'                 # Server hostname (or IP address)
DB_NAME = 'ARBotoxDB'                 # Your database name

DATABASE_URL = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'

engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()

def get_session():
    return SessionLocal()

def drop_tables():
    metadata.drop_all(engine)

def create_tables():
    metadata.create_all(engine)

def update_auto_increment(table_name, column_name):
    with engine.connect() as connection:
        max_query = text(f"SELECT MAX({column_name}) FROM {table_name}")
        result = connection.execute(max_query)
        max_value = result.scalar()  # Get the maximum value
        next_auto_increment = max_value + 100 if max_value is not None else 1

        alter_query = text(f"ALTER TABLE {table_name} AUTO_INCREMENT = {next_auto_increment}")
        connection.execute(alter_query)
        print(f"Successfully updated {table_name} AUTO_INCREMENT to {next_auto_increment}")

# Example usage for different tables
update_auto_increment('Patients', 'patient_id')
update_auto_increment('Clinicians', 'clinician_id')
update_auto_increment('Appointments', 'appointment_id')
update_auto_increment('TreatmentHistory', 'treatment_id')
update_auto_increment('TreatmentInfo', 'treatment_info_id')