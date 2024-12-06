from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import sessionmaker, relationship, joinedload, declarative_base
from datetime import datetime, date
import json
import pandas as pd

# Database connection details for MySQL
DB_USERNAME = 'root'  # Replace with your MySQL username
DB_PASSWORD = 'password'  # Replace with your MySQL password
DB_HOST = 'localhost'  # Server hostname (or IP address)
DB_NAME = 'ARBotoxDB'  # Your database name

DATABASE_URL = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'

engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Patient(Base):
    __tablename__ = 'Patients'
    patient_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    contact_info = Column(String(255))
    birthdate = Column(Date)
    medical_history = Column(Text)

    appointments = relationship('Appointment', back_populates='patient')


class Clinician(Base):
    __tablename__ = 'Clinicians'
    clinician_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

    appointments = relationship('Appointment', back_populates='clinician')


class Appointment(Base):
    __tablename__ = 'Appointments'
    appointment_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey('Patients.patient_id'))
    clinician_id = Column(Integer, ForeignKey('Clinicians.clinician_id'))
    appointment_date = Column(Date)
    location = Column(String(255))
    details = Column(Text)

    patient = relationship('Patient', back_populates='appointments')
    clinician = relationship('Clinician', back_populates='appointments')
    treatment_histories = relationship('TreatmentHistory', back_populates='appointment')


class TreatmentInfo(Base):
    __tablename__ = 'TreatmentInfo'
    treatment_info_id = Column(Integer, primary_key=True, autoincrement=True)
    treatment_name = Column(String(255), nullable=False)
    num_injections = Column(Integer)
    notes = Column(Text)

    treatment_histories = relationship('TreatmentHistory', back_populates='treatment_info')


class TreatmentHistory(Base):
    __tablename__ = 'TreatmentHistory'
    treatment_id = Column(Integer, primary_key=True, autoincrement=True)
    appointment_id = Column(Integer, ForeignKey('Appointments.appointment_id'))
    treatment_details = Column(Text)
    treatment_info_id = Column(Integer, ForeignKey('TreatmentInfo.treatment_info_id'))

    appointment = relationship('Appointment', back_populates='treatment_histories')
    treatment_info = relationship('TreatmentInfo', back_populates='treatment_histories')



class Landmark(Base):
    __tablename__ = 'Landmarks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    region_id = Column(Integer, ForeignKey('Regions.id'), nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    z = Column(Float)
    point_label = Column(Integer)
    visibility = Column(Integer)

    region = relationship('Region', back_populates='nodes')
    node_injections = relationship('NodeInjection', back_populates='node')


class Region(Base):
    __tablename__ = 'Regions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    side = Column(String(255))
    position = Column(String(255))
    area = Column(String(255))
    action = Column(String(255))
    origin = Column(String(255))
    insertion = Column(String(255))
    innervation = Column(String(255))

    nodes = relationship('Landmark', back_populates='region')
    region_injections = relationship('RegionInjection', back_populates='region')




class Injection(Base):
    __tablename__ = 'Injections'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mp_point = Column(Integer, nullable=False)
    treatment_type = Column(String(255), nullable=False)
    dosage = Column(Float, nullable=False)
    depth = Column(String(255), nullable=False)

    node_injections = relationship('NodeInjection', back_populates='injection')
    region_injections = relationship('RegionInjection', back_populates='injection')



class NodeInjection(Base):
    __tablename__ = 'NodeInjection'
    node_id = Column(Integer, ForeignKey('Landmarks.id'), primary_key=True)
    injection_id = Column(Integer, ForeignKey('Injections.id'), primary_key=True)

    node = relationship('Landmark', back_populates='node_injections')
    injection = relationship('Injection', back_populates='node_injections')


class RegionInjection(Base):
    __tablename__ = 'RegionInjections'
    region_id = Column(Integer, ForeignKey('Regions.id'), primary_key=True)
    injection_id = Column(Integer, ForeignKey('Injections.id'), primary_key=True)

    region = relationship('Region', back_populates='region_injections')
    injection = relationship('Injection', back_populates='region_injections')


class NodeRegion(Base):
    __tablename__ = 'LandmarkRegion'
    node_id = Column(Integer, ForeignKey('Landmarks.id'), primary_key=True)
    region_id = Column(Integer, ForeignKey('Regions.id'), primary_key=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    Base.metadata.create_all(bind=engine)

def add_patient(name, contact_info=None, birthdate=None, medical_history=None):
    session = SessionLocal()
    try:
        new_patient = Patient(
            name=name,
            contact_info=contact_info,
            birthdate=birthdate,
            medical_history=medical_history
        )
        session.add(new_patient)
        session.commit()
        session.refresh(new_patient)
        return new_patient
    finally:
        session.close()


def get_patient_by_id(patient_id):
    session = SessionLocal()
    try:
        patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
        return patient
    finally:
        session.close()

def search_patients(name_query):
    session = SessionLocal()
    try:
        patients = session.query(Patient).filter(Patient.name.like(f'%{name_query}%')).all()
        return patients
    finally:
        session.close()


def get_clinician_by_name(name):
    session = SessionLocal()
    try:
        clinician = session.query(Clinician).filter(Clinician.name == name).first()
        return clinician
    finally:
        session.close()


def add_clinician(name):
    session = SessionLocal()
    try:
        new_clinician = Clinician(name=name)
        session.add(new_clinician)
        session.commit()
        session.refresh(new_clinician)
        return new_clinician
    finally:
        session.close()

def schedule_appointment(patient_id, clinician_id, appointment_date, location=None, details=None):
    session = SessionLocal()
    try:
        new_appointment = Appointment(
            patient_id=patient_id,
            clinician_id=clinician_id,
            appointment_date=appointment_date,
            location=location,
            details=details
        )
        session.add(new_appointment)
        session.commit()
        session.refresh(new_appointment)
        return new_appointment
    finally:
        session.close()


def get_upcoming_appointments(patient_id):
    session = SessionLocal()
    try:
        now = datetime.now()
        appointments = session.query(Appointment) \
            .options(joinedload(Appointment.clinician)) \
            .filter(
            Appointment.patient_id == patient_id,
            Appointment.appointment_date >= now
        ).order_by(Appointment.appointment_date).all()
        return appointments
    finally:
        session.close()


def get_past_appointments(patient_id):
    session = SessionLocal()
    try:
        now = datetime.now()
        appointments = session.query(Appointment) \
            .options(joinedload(Appointment.clinician)) \
            .filter(
            Appointment.patient_id == patient_id,
            Appointment.appointment_date < now
        ).order_by(Appointment.appointment_date.desc()).all()
        return appointments
    finally:
        session.close()

def get_all_treatment_info():
    session = SessionLocal()
    try:
        treatments = session.query(TreatmentInfo).all()
        return treatments
    finally:
        session.close()


def add_treatment_info(treatment_name, num_injections, notes):
    session = SessionLocal()
    try:
        new_treatment = TreatmentInfo(
            treatment_name=treatment_name,
            num_injections=num_injections,
            notes=notes
        )
        session.add(new_treatment)
        session.commit()
        session.refresh(new_treatment)
        return new_treatment
    finally:
        session.close()


def add_treatment_history(appointment_id, treatment_details, treatment_info_id):
    session = SessionLocal()
    try:
        new_history = TreatmentHistory(
            appointment_id=appointment_id,
            treatment_details=treatment_details,
            treatment_info_id=treatment_info_id
        )
        session.add(new_history)
        session.commit()
        session.refresh(new_history)
        return new_history
    finally:
        session.close()


def get_treatment_history_by_appointment(appointment_id):
    session = SessionLocal()
    try:
        histories = session.query(TreatmentHistory) \
            .options(joinedload(TreatmentHistory.treatment_info)) \
            .filter(TreatmentHistory.appointment_id == appointment_id) \
            .all()
        return histories
    finally:
        session.close()



def insert_regions(session, regions_json):
    id_map = {}
    try:
        for region_data in regions_json:
            region = Region(
                name=region_data.get('name'),
                side=region_data.get('side'),
                position=region_data.get('position'),
                area=region_data.get('area'),
                action=region_data.get('action'),
                origin=region_data.get('origin'),
                insertion=region_data.get('insertion'),
                innervation=region_data.get('innervation')
            )
            session.add(region)
            session.flush()
            id_map[region_data['id']] = region.id
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error inserting regions: {e}")
    return id_map


def insert_nodes(session, nodes_json, region_id_map):
    id_map = {}
    try:
        for node_data in nodes_json:
            node = Landmark(
                region_id=region_id_map[node_data['region_id']],
                x=node_data['x'],
                y=node_data['y'],
                z=node_data.get('z'),
                point_label=node_data.get('point_label'),
                visibility=node_data.get('visibility')
            )
            session.add(node)
            session.flush()
            id_map[node_data['id']] = node.id
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error inserting nodes: {e}")
    return id_map




def insert_injections(session, injections_json):
    id_map = {}
    try:
        for injection_data in injections_json:
            injection = Injection(
                mp_point=injection_data['mp_point'],
                treatment_type=injection_data['treatment_type'],
                dosage=injection_data['dosage'],
                depth=injection_data['depth']
            )
            session.add(injection)
            session.flush()
            id_map[injection_data['id']] = injection.id
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error inserting injections: {e}")
    return id_map



def insert_node_injection(session, node_injections_json, node_id_map, injection_id_map):
    try:
        for li_data in node_injections_json:
            node_injection = NodeInjection(
                node_id=node_id_map[li_data['node_id']],
                injection_id=injection_id_map[li_data['injection_id']]
            )
            session.add(node_injection)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error inserting node injections: {e}")


def insert_region_injections(session, region_injections_json, region_id_map, injection_id_map):
    try:
        for ri_data in region_injections_json:
            region_injection = RegionInjection(
                region_id=region_id_map[ri_data['region_id']],
                injection_id=injection_id_map[ri_data['injection_id']]
            )
            session.add(region_injection)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error inserting region injections: {e}")


def insert_node_regions(session, node_regions_json, node_id_map, region_id_map):
    try:
        for lr_data in node_regions_json:
            node_region = NodeRegion(
                node_id=node_id_map[lr_data['node_id']],
                region_id=region_id_map[lr_data['region_id']]
            )
            session.add(node_region)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error inserting node regions: {e}")




def serialize_region(region):
    return {
        'id': region.id,
        'name': region.name,
        'side': region.side,
        'position': region.position,
        'area': region.area,
        'action': region.action,
        'origin': region.origin,
        'insertion': region.insertion,
        'innervation': region.innervation
    }


def serialize_node(node):
    return {
        'id': node.id,
        'region_id': node.region_id,
        'x': node.x,
        'y': node.y,
        'z': node.z,
        'point_label': node.point_label,
        'visibility': node.visibility
    }




def serialize_injection(injection):
    return {
        'id': injection.id,
        'mp_point': injection.mp_point,
        'treatment_type': injection.treatment_type,
        'dosage': injection.dosage,
        'depth': injection.depth
    }



def serialize_node_injection(node_injection):
    return {
        'node_id': node_injection.node_id,
        'injection_id': node_injection.injection_id
    }


def serialize_region_injection(region_injection):
    return {
        'region_id': region_injection.region_id,
        'injection_id': region_injection.injection_id
    }


def serialize_node_region(node_region):
    return {
        'node_id': node_region.node_id,
        'region_id': node_region.region_id
    }




def get_all_regions(session):
    regions = session.query(Region).all()
    return [serialize_region(region) for region in regions]


def get_all_nodes(session):
    nodes = session.query(Landmark).all()
    return [serialize_node(node) for node in nodes]




def get_all_injections(session):
    injections = session.query(Injection).all()
    return [serialize_injection(inj) for inj in injections]


def get_all_node_injections(session):
    node_injections = session.query(NodeInjection).all()
    return [serialize_node_injection(li) for li in node_injections]


def get_all_region_injections(session):
    region_injections = session.query(RegionInjection).all()
    return [serialize_region_injection(ri) for ri in region_injections]


def get_all_node_regions(session):
    node_regions = session.query(NodeRegion).all()
    return [serialize_node_region(lr) for lr in node_regions]

