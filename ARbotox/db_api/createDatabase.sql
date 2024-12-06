-- First, create the database
CREATE DATABASE ARBotoxDB;
USE ARBotoxDB;

-- INFORMATION REGARDING PATIENT'S

-- Note to Kevin from Edward
-- Focus on trying to get the functions for Natalie's table done first as that is the more important part. <- Kevin here, those json/db/pandas stuff should work. didnt finish the json to pandas thing tho.
-- As of right now, I don't think we really have a use for the treatmentInfo/treatmentHistory table in the GUI so just focus on the patient's table <- Bello! yeah i did nothing with that. and their respective tables.
--    since that is what Aiden is using.                                                                                                               
-- Ignore the complete mess I did in db.py (we can remove that honestly) <- its a whole new mess now! but it should work for the most part.             


CREATE TABLE Patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_info VARCHAR(255),
    birthdate DATE,
    medical_history TEXT
);

-- Clinicians Table
CREATE TABLE Clinicians (
    clinician_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Appointments Table
CREATE TABLE Appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    clinician_id INT,
    appointment_date DATE,
    location VARCHAR(255),
    details TEXT,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (clinician_id) REFERENCES Clinicians(clinician_id)
);

-- TreatmentInfo Table: generic treatment data
CREATE TABLE TreatmentInfo (
    treatment_info_id INT AUTO_INCREMENT PRIMARY KEY,
    treatment_name VARCHAR(255) NOT NULL,
    num_injections INT,
    notes TEXT
);

-- Treatment History Table: specific to each patient
CREATE TABLE TreatmentHistory (
    treatment_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT,
    treatment_details TEXT,
    treatment_info_id INT,
    FOREIGN KEY (treatment_info_id) REFERENCES TreatmentInfo(treatment_info_id),
    FOREIGN KEY (appointment_id) REFERENCES Appointments(appointment_id)
);


-- landmark table
CREATE TABLE Nodes (
   id INT PRIMARY KEY AUTO_INCREMENT,
   name VARCHAR(255) NOT NULL,
   side VARCHAR(255),
   region_id INT,
   x REAL NOT NULL,
   y REAL NOT NULL,
   z REAL,
   point INT NOT NULL
);
-- regions table
CREATE TABLE Regions (
   id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    side VARCHAR(255),
    area VARCHAR(255),
    segmentation JSON,
    action VARCHAR(255),
    origin VARCHAR(255),
    insertion VARCHAR(255),
    innervation VARCHAR(255)
);
-- injection table
CREATE TABLE Injections (
   id INT PRIMARY KEY AUTO_INCREMENT,
   point INT NOT NULL,
   name VARCHAR(255) NOT NULL,
   treatment_type VARCHAR(255) NOT NULL,  -- 4 types:Botox (Allergan), Dysport(Galderma), Xeomin(merz), Jeuveau(Evolus)
   side_effects VARCHAR(255) NOT NULL,
   desired_outcome VARCHAR(255) NOT NULL,
   dosage DECIMAL(5, 2) NOT NULL,         --  in units for toxins or ml for fillers
   depth VARCHAR(255) NOT NULL           -- 2:Intramuscular Injection / Subcutaneous Injection
);
CREATE TABLE NodeInjections (
   node_id INT NOT NULL,
   injection_id INT NOT NULL,
   PRIMARY KEY (node_id, injection_id),
   FOREIGN KEY (node_id) REFERENCES Nodes(id) ON DELETE CASCADE,
   FOREIGN KEY (injection_id) REFERENCES Injections(id) ON DELETE CASCADE
);
-- region injection table
CREATE TABLE RegionInjections (
   region_id INT NOT NULL,
   injection_id INT NOT NULL,
   PRIMARY KEY (region_id, injection_id),
   FOREIGN KEY (region_id) REFERENCES Regions(id) ON DELETE CASCADE,
   FOREIGN KEY (injection_id) REFERENCES Injections(id) ON DELETE CASCADE
);
-- landmarkregion table
CREATE TABLE NodeRegion (
   node_id INT NOT NULL,
   region_id INT NOT NULL,
   PRIMARY KEY (node_id, region_id),
   FOREIGN KEY (node_id) REFERENCES Nodes(id),
   FOREIGN KEY (region_id) REFERENCES Regions(id)
);




