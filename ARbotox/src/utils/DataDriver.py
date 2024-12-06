import src.repository.AnatomyRepository as repo
import src.utils.Values as values
import pandas as pd
import ast
from db_api.Id_fix import get_session
from src.repository.AnatomyRepository import Region, Node, Injection
import src.repository.AnatomyRepository as repo
from db_api.Id_fix import get_session, drop_tables, create_tables
session = get_session()
import src.utils.Values as values

class DataDriver:


    @classmethod
    def initialize_df_and_db_data(cls, reload_data_to_database=False):
        nodes_data, regions_data, injections_data = DataDriver.load_csv()
        if reload_data_to_database:
            drop_tables()
            create_tables()
            DataDriver.save_to_database(session, nodes_data, regions_data, injections_data)
        nodes_df, regions_df, injections_df = DataDriver.from_database_to_df(session)
        region_injections_df, node_injection_df, node_region_df = DataDriver.create_relationships(regions_df, nodes_df, injections_df)
        if reload_data_to_database:
            DataDriver.save_relationships_to_database(session, region_injections_df, node_injection_df, node_region_df)
        return nodes_df, regions_df, injections_df, node_injection_df, region_injections_df, node_region_df

    @classmethod
    def load_mapped_landmarks(cls):
        mapping_df = pd.read_csv(values.FilePaths.map_nodes_region, converters={
            'landmark': ast.literal_eval,
            'landmark_coords': ast.literal_eval,
            'segmentation': ast.literal_eval})
        mapped_landmarks_df = mapping_df[['segmentation', 'landmark', 'landmark_coords', 'name']].copy()
        return mapped_landmarks_df

    @classmethod
    def load_entities(cls, regions_df, nodes_df, injections_df):
        regions = Region.initialize_regions(regions_df)
        nodes = Node.initialize_nodes(nodes_df)
        injections = Injection.initialize_injections(injections_df)
        return regions, nodes, injections

    @classmethod
    def load_csv(cls, nodes_file_path=values.FilePaths.nodes_data,
                 regions_file_path=values.FilePaths.region_data,
                 injections_file_path=values.FilePaths.injections_data):
        # Read the Csvs
        try:
            nodes_data = pd.read_csv(values.FilePaths.nodes_data)
            regions_data = pd.read_csv(values.FilePaths.region_data)
            injections_data = pd.read_csv(values.FilePaths.injections_data)
            nodes_data.sort_values(by=['point'], inplace=True)
            log(".csv data loaded!")
            return nodes_data, regions_data, injections_data
        except Exception as e:
            log("Exception while loading data from csv file", e)

    @classmethod
    def save_to_database(cls, session, nodes_data, regions_data, injections_data):
        try:
            repo.save_nodes_df_to_db(session, nodes_data)
            repo.save_regions_df_to_db(session, regions_data)
            repo.save_injections_df_to_db(session, injections_data)
            log("Data saved to database!")
        except Exception as e:
            log("Exception while saving data into database", e)

    @classmethod
    def match_regions_to_nodes(cls, nodes_df, regions_df, session):
        sub_regions = regions_df[['id', 'name']].rename(columns={'id': 'region_id'})
        merged_df = nodes_df.merge(sub_regions, on='name', how='left')
        nodes_df['region_id'] = merged_df['region_id_y']
        for _, row in nodes_df.iterrows():
            node_to_update = session.query(repo.Node).filter_by(id=row['id']).first()
            if node_to_update:
                node_to_update.region_id = row['region_id']
                node_to_update.name = row['name']
                node_to_update.side = row['side']
                node_to_update.x = row['x']
                node_to_update.y = row['y']
                node_to_update.z = row['z']
            node_to_update.point = row['point']
        try:
            session.commit()
            log('Matched regions to nodes successfully.')
        except Exception as e:
            session.rollback()
            log("Exception while saving data into the database", e)
        return nodes_df

    @classmethod
    def from_database_to_df(cls, session):
        try:
            nodes_df = repo.get_all_nodes(session)
            regions_df = repo.get_all_regions(session)
            injections_df = repo.get_all_injections(session)
            nodes_df = DataDriver.match_regions_to_nodes(nodes_df, regions_df, session)
            log("Data loaded from database!")
            return nodes_df, regions_df, injections_df
        except Exception as e:
            log("Exception while loading data from database", e)

    @classmethod
    def relation_from_database_to_df(cls, session):
        node_injections = repo.get_all_node_injections(session)
        region_injections = repo.get_all_region_injections(session)
        node_regions = repo.get_all_node_regions(session)
        df_node_injections = pd.DataFrame(node_injections)
        df_region_injections = pd.DataFrame(region_injections)
        df_node_regions = pd.DataFrame(node_regions)
        return df_node_injections, df_region_injections, df_node_regions

    @classmethod
    def create_relationships(cls, regions_df, nodes_df, injections_df):
        # Create Relationships.
        try:
            region_injection_df = repo.generate_region_injection_relationships_df(regions_df, injections_df)
            node_region_df = repo.generate_node_region_relationships_df(nodes_df, regions_df)
            node_injection_df = repo.generate_node_injection_relationships_df(nodes_df, injections_df)
            return region_injection_df, node_injection_df, node_region_df
            log("Relationships created!")
        except Exception as e:
            log("Exception while creating relationships", e)

    @classmethod
    def save_relationships_to_database(cls, session, region_injection_df, node_injection_df, node_region_df):
        # Save Relationships to DB.
        try:
            repo.save_region_injections_df_to_db(session, region_injection_df)
            repo.save_node_regions_df_to_db(session, node_region_df)
            repo.save_node_injections_df_to_db(session, node_injection_df)
            log("Relationships saved to database!")
        except Exception as e:
            log("Exception while saving relationships to database", e)


def log(message, *args):
    print(f"\n----[ARBotox @ DataDriver]: {message} {args}")
