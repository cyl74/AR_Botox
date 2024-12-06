from typing import List
import pandas as pd
import numpy as np
import src.utils.Values as values

"""
A landmark point
"""
import pandas as pd

class Landmark:
    def __init__(self):
        self.point = None
        self.region = None
        self.side = None
        self.injectable = False
        self.injections = []
        self.coordinate = None



"""
Class Injection
    Define injections with their name and their injection site via a point.
"""
class Injection:
    name = None
    dosage = None
    desired_outcome = None
    treatment_type = None
    depth = None
    side_effects = None

    def load_landmarks(self):
        if not landmarks.empty:
            for _, row in filtered_landmarks.iterrows():
                injection = Injection()
                injection.name = row['name']
                injection.dosage = row['dosage']
                injection.side_effects = row['side_effects']
                injection.treatment_type = row['treatment_type']
                injection.depth = row['depth']
                injection.desired_outcome = row['desired_outcome']
                self.injections.append(injection)
                print(injection.name)
            self.injectable = True


class Area:
    name = "AREA"
    def __init__(self, name):
        self.name = name
"""
Class Region
    Create a class for each anatomical region on the face.
    name : example, LEFT_EYE, RIGHT_EYE
    connections : list of Connection objects which represent nodes
    injection_points : a list of Injection objects 
"""
class Region:
    name = "REGION"
    name_id = None
    coordinates = []
    area = []
    side = None
    nodes: list[Node] = list()
    injection_points: list[Node] = list()

    landmarks_df = pd.read_csv(Values.FilePaths.landmark_data)

    def __init__(self):
        self.load_nodes_in_region()

    def get(self):
        return self.name, self.nodes, self.injection_points

    def load_nodes_in_region(self):
        """
        Load the nodes defined in the region from the csv file.
        """
        import pandas as pd
        self.landmarks_df.sort_values(by='landmark', ascending=True, inplace=True)
        filtered_landmarks = self.landmarks_df[self.landmarks_df['name'] == self.name_id]

        for _, row in filtered_landmarks.iterrows():
            node = Node()
            node.point = row['landmark']
            node.load_injections()
            node.side = row['side']
            node.region = row['name']
            node.landmark_coords = row['landmark_coords']

            # TODO: Handle injection_point logic
            # if row.get('injection_point', False):
            #     node.injectable = True
            node.injection_point = None  # Placeholder for now`
            self.nodes.append(node)

class AnatomyMap:
    regions: list[Region] = list()

    regions_df = pd.read_csv(Values.FilePaths.region_data)

    def __init__(self):
        self.load_regions_data()

    def print_all_values(self):
        for region in self.regions:
            for attr, value in vars(region).items():
                print(f'{attr}: {value}')

    def load_regions_data(self):
        for _, row in self.regions_df.iterrows():
            region = Region()
            region.name_id = row['name']
            region.name = row['region_name']
            region.area = Area(row['area'])
            region.coordinates = row['segmentation']
            self.regions.append(region)
