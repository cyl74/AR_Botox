# Mapping of regions to their general areas
"""
Store any global constants and references here.
"""

class FilePaths:
    image_reference_mp_data = 'data/inputs/mediapipe_landmarks_from_image.csv'
    keypoint_data = 'data/inputs/train_keypoints.csv'
    segment_data = 'data/inputs/train_segments.csv'
    nodes_data = 'data/inputs/nodes.csv'
    region_data = 'data/inputs/regions.csv'
    map_nodes_region = 'data/inputs/map_nodes_in_region.csv' # 478 rows
    injections_data = 'data/inputs/injections.csv'


class AnatomyDictionary:
    region_to_area = {
        "Cheek": [
            "risorius",
            "buccinator",
            "zygomaticus_minor",
            "zygomaticus_major"
        ],
        "Jaw": [
            "depressor_anguli_oris",
            "masseter"
        ],
        "Masseter": [
            "masseter"
        ],
        "Nose": [
            "depressor_septi_nasi",
            "nasalis_transverse",
            "compressor_narium_minor",
            "nasalis_alar",
            "dilator_naris_anterior",
            "procerus",
            "radix",
            "nose_tip",
            "columella"
        ],
        "Eye": [
            "orbital_oculi",
            "orbiculi_pelperbal",
            "lateral_palpebral_ligament",
            "medial_palpebral_ligament"
        ],
        "Forehead": [
            "corrugator_supercilii",
            "frontalis"
        ],
        "Temples": [
            "temporalis"
        ],
        "Lips": [
            "obicularis_oris",
            "philtral_columns",
            "tubercles_upper",
            "tubercles_lower",
            "oral_commissure",
            "vermillion_upper",
            "cupids_bow",
            "vermillion_lower"
        ],
        "Chin": [
            "mentalis",
            "depressor_anguli_oris",
            "depressor_labii_inferioris"
        ],
        "Upper lip": [
            "levator_labii_superioris_alaque_nasi",
            "levator_labii_superioris"
        ],
        "Lower lip": [
            "depressor_labii_inferioris",
            "tubercles_lower"
        ]
    }

# Example for accessing
# region_to_area["Cheek"] will give the list of muscles in the "Cheek" region
