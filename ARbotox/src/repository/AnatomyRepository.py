
from sqlalchemy import Column, Integer, Float, ForeignKey, String, Text, JSON
from sqlalchemy.orm import relationship
from db_api.Id_fix import Base
from sqlalchemy.orm import registry
import pandas as pd
import json
mapper_registry = registry()


class Node(Base):
    __tablename__ = 'Nodes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    region_id = Column(Integer, ForeignKey('Regions.id'), nullable=False)
    name = Column(String(255), nullable=False)
    side = Column(String(255))
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    z = Column(Float)
    point = Column(Integer)

    region = relationship('Region', back_populates='node')
    node_injections = relationship('NodeInjection', back_populates='node')

    def get_by_point(cls, session, point):
        return session.query(cls).filter_by(point=point).first()

    @classmethod
    def initialize_nodes(self, nodes_df):
        nodes_map = {}
        print(nodes_df)
        for _, row in nodes_df.iterrows():
            node = Node(
                id=row['id'],
                region_id=row['region_id'],
                name=row['name'],
                side=row['side'],
                x=row['x'],
                y=row['y'],
                z=row['z'],
                point=row['point']
            )
            nodes_map[node.name.lower()] = node
        return nodes_map

class Region(Base):
    __tablename__ = 'Regions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    area = Column(String(255))
    segmentation = Column(JSON)
    action = Column(String(255))
    origin = Column(String(255))
    insertion = Column(String(255))
    innervation = Column(String(255))

    node = relationship('Node', back_populates='region')
    region_injections = relationship('RegionInjection', back_populates='region')

    @classmethod
    def initialize_regions(self, regions_df):
        regions_map = {}
        for _, row in regions_df.iterrows():
            region = Region(
                id=row['id'],
                name=row['name'],
                area=row['area'],
                action=row['action'],
                origin=row['origin'],
                insertion=row['insertion'],
                innervation=row['innervation'])
            regions_map[region.name.lower()] = region
        return regions_map


class Injection(Base):
    __tablename__ = 'Injections'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    point = Column(Integer, nullable=False)
    treatment_type = Column(String(255), nullable=False)
    dosage = Column(Float, nullable=False)
    depth = Column(String(255), nullable=False)
    desired_outcome = Column(String(255), nullable=True)  # Added for consistency with .sql
    side_effects = Column(Text, nullable=True)

    node_injections = relationship('NodeInjection', back_populates='injection')
    region_injections = relationship('RegionInjection', back_populates='injection')

    @classmethod
    def initialize_injections(self, injections_df):
        injections_map = {}
        for _, row in injections_df.iterrows():
            injection = Injection(
                id=row['id'],
                name=row['name'],
                point=row['point'],
                treatment_type=row['treatment_type'],
                dosage=row['dosage'],
                depth=row['depth'],
                desired_outcome=row['desired_outcome'],
                side_effects=row['side_effects'])
            injections_map[injection.name.lower()] = injection
        return injections_map

    def return_keys(self, injections):
        print(injections.keys())
        return injections.keys()


class NodeInjection(Base):
    __tablename__ = 'NodeInjections'
    node_id = Column(Integer, ForeignKey('Nodes.id'), primary_key=True)
    injection_id = Column(Integer, ForeignKey('Injections.id'), primary_key=True)

    node = relationship('Node', back_populates='node_injections')
    injection = relationship('Injection', back_populates='node_injections')


class RegionInjection(Base):
    __tablename__ = 'RegionInjections'
    region_id = Column(Integer, ForeignKey('Regions.id'), primary_key=True)
    injection_id = Column(Integer, ForeignKey('Injections.id'), primary_key=True)

    region = relationship('Region', back_populates='region_injections')
    injection = relationship('Injection', back_populates='region_injections')


class NodeRegion(Base):
    __tablename__ = 'NodeRegion'
    node_id = Column(Integer, ForeignKey('Nodes.id'), primary_key=True)
    region_id = Column(Integer, ForeignKey('Regions.id'), primary_key=True)


# HELPERS
def serialize_region(region):
    return {
        'id': getattr(region, 'id', None),
        'name': getattr(region, 'name', None),
        'area': getattr(region, 'area', None),
        'action': getattr(region, 'action', None),
        'origin': getattr(region, 'origin', None),
        'insertion': getattr(region, 'insertion', None),
        'innervation': getattr(region, 'innervation', None)
    }


def serialize_node(node):
    return {
        'id': getattr(node, 'id', None),
        'region_id': getattr(node, 'region_id', None),
        'point': getattr(node, 'point', None),
        'side': getattr(node, 'side', None),
        'name': getattr(node, 'name', None),
        'x': getattr(node, 'x', None),
        'y': getattr(node, 'y', None),
        'z': getattr(node, 'z', None),
    }


def serialize_injection(injection):
    return {
        'id': getattr(injection, 'id', None),
        'name': getattr(injection, 'name', None),
        'point': getattr(injection, 'point', None),
        'treatment_type': getattr(injection, 'treatment_type', None),
        'dosage': getattr(injection, 'dosage', None),
        'depth': getattr(injection, 'depth', None),
        'desired_outcome' : getattr(injection, 'desired_outcome', None),
        'side_effects': getattr(injection, 'side_effects', None),
    }


def serialize_node_injection(node_injection):
    return {
        'node_id': getattr(node_injection, 'node_id', None),
        'injection_id': getattr(node_injection, 'injection_id', None)
    }


def serialize_region_injection(region_injection):
    return {
        'region_id': getattr(region_injection, 'region_id', None),
        'injection_id': getattr(region_injection, 'injection_id', None)
    }


def serialize_node_region(node_region):
    return {
        'node_id': getattr(node_region, 'node_id', None),
        'region_id': getattr(node_region, 'region_id', None)
    }

# GETTERS -> TO PANDAS DB
def get_all_regions(session):
    regions = session.query(Region).all()
    serialized = [serialize_region(region) for region in regions]
    log("Returning regions as Dataframe.")
    df = pd.DataFrame(serialized)
    print(df)
    return pd.DataFrame(serialized)

def get_all_nodes(session):
    nodes = session.query(Node).all()
    serialized = [serialize_node(node) for node in nodes]
    log("Returning nodes as Dataframe.")
    df = pd.DataFrame(serialized)
    print(df.keys())
    print(df)
    return df

def get_all_injections(session):
    injections = session.query(Injection).all()
    serialized = [serialize_injection(inj) for inj in injections]
    log("Returning injections as Dataframe.")
    df = pd.DataFrame(serialized)
    print(df)
    return df

def get_all_node_injections(session):
    node_injections = session.query(NodeInjection).all()
    serialized = [serialize_node_injection(li) for li in node_injections]
    df = pd.DataFrame(serialized)
    log("Returning node-injections as Dataframe.")
    print(df)
    return df

def get_all_region_injections(session):
    region_injections = session.query(RegionInjection).all()
    serialized = [serialize_region_injection(ri) for ri in region_injections]
    df = pd.DataFrame(serialized)
    log("Returning region-injections as Dataframe.")
    print(df)
    return df

def get_all_node_regions(session):
    node_regions = session.query(NodeRegion).all()
    serialized = [serialize_node_region(lr) for lr in node_regions]
    df = pd.DataFrame(serialized)
    log("Returning node-regions as Dataframe.")
    print(df)
    return df


def get_all_node_injections(session):
    node_injections = session.query(NodeInjection).all()
    return [serialize_node_injection(li) for li in node_injections]

def get_all_region_injections(session):
    region_injections = session.query(RegionInjection).all()
    return [serialize_region_injection(ri) for ri in region_injections]

def get_all_node_regions(session):
    node_regions = session.query(NodeRegion).all()
    return [serialize_node_region(lr) for lr in node_regions]


# SAVERS: DIRECTLY PANDAS -> DB
def save_injections_df_to_db(session, dataframe):
    dataframe = dataframe.where(pd.notnull(dataframe), None)

    try:
        for _, row in dataframe.iterrows():
            injection = Injection(
                name=row['name'],
                point=row['point'],
                treatment_type=row['treatment_type'],
                desired_outcome=row['desired_outcome'],
                dosage=row['dosage'],
                depth=row['depth'],
                side_effects=row.get('side_effects', None))
            session.add(injection)
            session.flush()
        session.commit()
        log("Injections .csv file saved successfully into the database.")
    except Exception as e:
        session.rollback()
        log(f"Error saving injections: {e}")
    finally:
        session.close()


def save_nodes_df_to_db(session, dataframe):
    try:
        dataframe['region_id'] = dataframe['region_id'].fillna(-1)
        dataframe['z'] = pd.to_numeric(dataframe['z'], errors='coerce')
        dataframe['z'].fillna(0.0, inplace=True)
        if dataframe.isna().any().any():
            dataframe.fillna("none", inplace=True)
        for _, row in dataframe.iterrows():
            node = Node(
                region_id=row['region_id'],
                name=row['name'],
                side=row['side'],
                x=row['x'],
                y=row['y'],
                z=row.get('z', None),
                point=row.get('point', None),
            )
            session.add(node)
            session.flush()
        session.commit()
        print("Nodes saved successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error saving nodes: {e}")
    finally:
        session.close()



def save_regions_df_to_db(session, dataframe):
    if dataframe.isna().any().any():
        dataframe.fillna("none", inplace=True)
    try:
        for _, row in dataframe.iterrows():
            segmentation_json = json.dumps({
                "segmentation": row['segmentation']
            })
            region = Region(
                name=row['name'],
                area=row['area'],
                segmentation=segmentation_json,  # Save as JSON
                action=row['action'],
                origin=row['origin'],
                insertion=row['insertion'],
                innervation=row['innervation']
            )
            session.add(region)
        session.commit()
        log("Regions DataFrame successfully saved into the database.")
    except Exception as e:
        session.rollback()
        log(f"Error saving regions: {e}")


# RELATIONALS - Suggested to Serialize individual DFs from DB first then generate Relational DFs
def generate_node_injection_relationships_df(nodes_df, injections_df):
    relationships_df = pd.merge(nodes_df, injections_df, on='point', suffixes=('_node', '_injection'))
    relationships_df = relationships_df[['id_node', 'id_injection']].rename(
        columns={'id_node': 'node_id', 'id_injection': 'injection_id'})
    log("Generating node-injection relationships dataframe.")
    print(relationships_df)
    return relationships_df


def generate_node_region_relationships_df(nodes_df, regions_df):
    try:
        if 'name' not in nodes_df.columns or 'name' not in regions_df.columns:
            raise ValueError("Both DataFrames must have a 'name' column for matching.")
        merged_df = pd.merge(nodes_df, regions_df, on='name', suffixes=('_node', '_region'))
        nodes_df = nodes_df.merge(
            merged_df[['name', 'id_region']], on='name', how='left'
        )
        nodes_df.drop('region_id', axis=1, inplace=True)
        nodes_df.rename(columns={'id_region': 'region_id'}, inplace=True)
        nodes_df['region_id'] = nodes_df['region_id'].fillna(-1).astype(int)
        log("Successfully assigned region_id to nodes based on name matching.")
        print(nodes_df)
        return nodes_df
    except Exception as e:
        log(f"Error assigning region_id to nodes: {e}")
        raise


def generate_region_injection_relationships_df(regions_df, injections_df):
    try:
        merged_df = pd.merge(injections_df, regions_df, on='name', suffixes=('_injection', '_region'))
        relationships_df = merged_df[['id_region', 'id_injection']].rename(
            columns={'id_region': 'region_id', 'id_injection': 'injection_id'})
        log("Successfully generated region-injection relationships dataframe.")
        print(relationships_df)
        return relationships_df
    except Exception as e:
        log(f"Error generating region-injection relationships: {e}")
        raise


def save_region_injections_df_to_db(session, relationships_df):
    try:
        relationships = [
            RegionInjection(
                region_id=row['region_id'],
                injection_id=row['injection_id'])
            for _, row in relationships_df.iterrows()]
        session.bulk_save_objects(relationships)
        session.commit()
        print("Region-Injection relationships saved successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error saving Region-Injection relationships: {e}")


def save_node_regions_df_to_db(session, relationships_df):
    try:
        relationships = [
            NodeRegion(
                node_id=row['id'],
                region_id=row['region_id'])
            for _, row in relationships_df.iterrows() ]
        session.bulk_save_objects(relationships)
        session.commit()
        print("Node-Region relationships saved successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error saving Node-Region relationships: {e}")


def save_node_injections_df_to_db(session, node_injections_df):
    try:
        node_injections = [
            NodeInjection(node_id=row['node_id'], injection_id=row['injection_id'])
            for _, row in node_injections_df.iterrows()]
        session.bulk_save_objects(node_injections)
        session.commit()
        log("Node-injection relationships saved successfully.")
    except Exception as e:
        session.rollback()
        log(f"Error saving node-injection relationships: {e}")
    finally:
        session.close()

    all_regions = get_all_regions(session)
    all_nodes = get_all_nodes(session)
    all_injections = get_all_injections(session)
    all_node_injections = get_all_node_injections(session)
    all_region_injections = get_all_region_injections(session)
    all_node_regions = get_all_node_regions(session)

def log(message, *args):
    print(f"\n----[ARBotoxDB @ Repository]: {message} {args}")
