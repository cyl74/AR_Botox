import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks.python.vision import FaceLandmarker
import numpy as np
import cv2
import ast
import src.utils.TextModifier as TextModifier
import pandas as pd

from src.repository.AnatomyRepository import Region
from src.utils.DataDriver import DataDriver
from db_api.Id_fix import get_session, drop_tables, create_tables
import cv2
import matplotlib.pyplot as plt
from matplotlib import cm
import re
session = get_session()


def normalize_string(s):
    if isinstance(s, str):
        s = s.replace('’', "'").replace('‘', "'")
        s = re.sub(r'\s+', ' ', s.strip())
    return s


class DrawOptions:
    def __init__(self, landmark_range=None, landmark_labels=False,
                 general_area=None, regions=[],
                 treatment_type=None,
                 draw_all_injections=False,
                 draw_all_labels=False,
                 draw_tesselations=True,
                 draw_all_regions=False):


        self.general_area = general_area
        self.regions = regions
        self.treatment_type = treatment_type
        self.draw_all_injections = draw_all_injections
        self.draw_all_labels = draw_all_labels
        self.draw_tesselations = draw_tesselations
        self.draw_all_regions = draw_all_regions

    def apply_draw_options(self, df, injections_map=None, regions_map=None, nodes_map=None,
                           node_injections_df=None, region_injections_df=None, node_regions_df=None):
        def parse(value):
            return normalize_string(value).lower()

        regions_map_parsed = {parse(key): value for key, value in regions_map.items()} if regions_map else {}
        injections_map_parsed = {parse(key): value for key, value in injections_map.items()} if injections_map else {}
        nodes_map_parsed = {parse(key): value for key, value in nodes_map.items()} if nodes_map else {}
        resolved_regions = [regions_map_parsed[parse(region)] for region in self.regions if
                            parse(region) in regions_map_parsed] if self.regions and regions_map else []
        resolved_region_ids = [region.id for region in resolved_regions]
        region_nodes_df_filtered = node_regions_df[node_regions_df['region_id'].isin(resolved_region_ids)] \
            if resolved_regions and node_regions_df is not None and not node_regions_df.empty else pd.DataFrame()
        node_injections_df_filtered = node_injections_df[
            node_injections_df['node_id'].isin(region_nodes_df_filtered['id'])
        ] if not region_nodes_df_filtered.empty and node_injections_df is not None and not node_injections_df.empty else pd.DataFrame()

        injections_to_nodes = {}
        for _, row in node_injections_df_filtered.iterrows():
            injections_to_nodes.setdefault(row['injection_id'], []).append(row['node_id'])

        injection_id_to_region = \
            node_injections_df_filtered.merge(region_nodes_df_filtered, left_on='node_id', right_on='id', how='inner') \
                [['injection_id', 'region_id']].drop_duplicates().set_index('injection_id')['region_id'].to_dict() \
                if not node_injections_df_filtered.empty else {}

        if 'id' in df.columns:
            valid_nodes = region_nodes_df_filtered['id'].tolist() if not region_nodes_df_filtered.empty else []

            # filter the rows that match valid nodes or resolved regions
            df_filtered = df[df['id'].isin(valid_nodes)] if valid_nodes else pd.DataFrame()

            if not node_injections_df_filtered.empty:
                df_filtered = df_filtered.merge(
                    node_injections_df_filtered[['node_id', 'injection_id']],
                    left_on='id',
                    right_on='node_id',
                    how='outer'  # Include all rows from df_filtered and node_injections_df_filtered
                )
                # region_id to injection_id
                df_filtered['region_id'] = df_filtered['injection_id'].map(injection_id_to_region)
            # treatment type for matched injections
            df_filtered['treatment_type'] = df_filtered['injection_id'].map(
                lambda inj_id: getattr(injections_map_parsed.get(str(inj_id)), 'treatment_type', None)
            )

            resolved_region_names = [region.name for region in resolved_regions]
            all_regions_df = pd.DataFrame({'name': resolved_region_names})
            all_regions_df['name'] = all_regions_df['name'].apply(parse)
            df_filtered['name'] = df_filtered['name'].apply(parse)
            df_filtered = df_filtered[df_filtered['name'].isin(all_regions_df['name'])].reset_index(drop=True)
            nodes_with_coords = df[['id', 'x', 'y']].rename(columns={'id': 'node_id'})
            df_filtered = df_filtered.merge(nodes_with_coords, on='node_id', how='left')

            df_filtered['treatment_type'] = df_filtered['treatment_type'].combine_first(
                df_filtered['injection_id'].map(
                    lambda inj_id: getattr(injections_map_parsed.get(str(inj_id)), 'treatment_type', None)
                    if pd.notna(inj_id) else None
                ).combine_first(
                    df_filtered['name'].map(
                        lambda name: getattr(injections_map_parsed.get(parse(name)), 'treatment_type', None)
                        if pd.notna(name) else None
                    )
                )
            )

            df_filtered.drop(columns=['x_y', 'y_y','node_id','region_id','face_idx'], inplace=True)
            df_filtered.rename(columns={'x_x': 'x', 'y_x':'y'}, inplace=True)
        else:
            # Default to an empty DataFrame if the 'id' column is missing
            df_filtered = pd.DataFrame()

        #print("=== Debugging Information ===")
        #print("Resolved Regions:", [region.name for region in resolved_regions])
        #print("Filtered Regions in DataFrame:", df_filtered['name'].unique() if not df_filtered.empty else [])
        #print("Filtered DataFrame After Mapping Treatment Type:")
        #print(df_filtered[['id','point','side','name','x','y','z','injection_id','treatment_type']])
        #print("============================")
        return df_filtered


class ArBotox:
    nodes_df = None
    injections_df = None
    regions_df = None
    mapping_df = None
    mapped_nodes_df = None

    regions_map = None
    nodes_map = None
    injections_map = None
    node_injections_map = None
    region_injections_map = None
    node_regions_map = None
    mapped_nodes_df = None

    def __init__(self, reload_data_to_database=False):
        self.nodes_df, self.regions_df, self.injections_df, self.node_injections_map, self.region_injections_map, self.node_regions_map = DataDriver.initialize_df_and_db_data(reload_data_to_database)
        self.regions_map, self.nodes_map, self.injections_map,  = DataDriver.load_entities(self.regions_df,
                                                                                           self.nodes_df,
                                                                                           self.injections_df)

        self.mapped_nodes_df = DataDriver.load_mapped_landmarks()

    class FaceLandmarker:
        mediapipe_base_options = None
        face_landmarker = None
        face_landmarker_options = None
        base_options = None
        options = None
        detector: FaceLandmarker.create_from_options

        def __init__(self, num_faces=1, min_detection_confidence=0.6, min_track_confidence=0.6):
            self.base_options = mp.tasks.BaseOptions(model_asset_path='task/face_landmarker.task')
            self.options = mp.tasks.vision.FaceLandmarkerOptions(base_options=self.base_options,
                                                                 output_face_blendshapes=True,
                                                                 output_facial_transformation_matrixes=True,
                                                                 num_faces=num_faces,
                                                                 min_face_detection_confidence=min_detection_confidence,
                                                                 min_tracking_confidence=min_track_confidence)
            self.detector = FaceLandmarker.create_from_options(self.options)

    landmark_label_text_mod = TextModifier.landmark_point_text_mod
    landmark_start_text_mod = TextModifier.landmark_start_text_mod
    landmark_end_text_mod = TextModifier.landmark_end_text_mod
    landmark_injection_text_mod = TextModifier.landmark_injection_text_mod
    draw_spec_tesselation = TextModifier.TextModifier.draw_spec_tesselation

    face_landmarker = FaceLandmarker()

    def landmarks_to_dataframe(self, face_landmarks_list, frame, nodes_df):
        height, width, _ = frame.shape

        detected_points = {point_idx for face_landmarks in face_landmarks_list for point_idx, _ in
                           enumerate(face_landmarks)}
        nodes_df_filtered = nodes_df[nodes_df['point'].isin(detected_points)].copy()

        updated_points = []
        updated_x = []
        updated_y = []
        updated_z = []
        updated_face_idx = []

        # Iterate over face_landmarks_list and collect data in lists
        for idx, face_landmarks in enumerate(face_landmarks_list):
            for point_idx, landmark in enumerate(face_landmarks):
                if point_idx in detected_points:
                    x_coord = landmark.x * width
                    y_coord = landmark.y * height
                    z_coord = landmark.z

                    updated_points.append(point_idx)
                    updated_x.append(x_coord)
                    updated_y.append(y_coord)
                    updated_z.append(z_coord)
                    updated_face_idx.append(idx)

        updated_data = pd.DataFrame({
            'point': updated_points,
            'x': updated_x,
            'y': updated_y,
            'z': updated_z,
            'face_idx': updated_face_idx
        })

        nodes_df_filtered = pd.merge(nodes_df_filtered, updated_data, on='point', how='left', suffixes=('', '_new'))

        for col in ['x', 'y', 'z']:
            if f"{col}_new" in nodes_df_filtered.columns:
                nodes_df_filtered[col] = nodes_df_filtered[f"{col}_new"]
                nodes_df_filtered.drop(columns=[f"{col}_new"], inplace=True)

        return nodes_df_filtered

    def detect_and_draw(self, width, height, frame, draw_options: DrawOptions):

        detection_result = self.face_landmarker.detector.detect(frame)
        if detection_result is None or detection_result.face_landmarks is None:
            return frame

        annotated_image = np.copy(frame.numpy_view())
        face_landmarks_list = detection_result.face_landmarks

        detected_landmarks_list = [
            {point: (landmark.x, landmark.y) for point, landmark in enumerate(face_landmarks)}
            for face_landmarks in face_landmarks_list
        ]

        df_landmarks = self.landmarks_to_dataframe(face_landmarks_list, annotated_image, self.nodes_df)
        df_filtered = draw_options.apply_draw_options(
            df_landmarks, regions_map=self.regions_map, nodes_map=self.nodes_map, injections_map=self.injections_map,
        region_injections_df=self.region_injections_map, node_regions_df=self.node_regions_map, node_injections_df=self.node_injections_map)

        # DRAW REGIONS
        annotated_image = self.project_polygons(frame=annotated_image, height=width, width=height, face_landmarks_list=detected_landmarks_list,
                                                filtered_df=df_filtered,regions_to_plot=draw_options.regions, draw_options=draw_options)

        # DRAW LANDMARKS
        self.draw_points(df_filtered, annotated_image, draw_options,
                         node_injections_df=self.node_injections_map, region_injections_df=self.region_injections_map,
                         node_regions_df=self.node_regions_map
                )

        if draw_options.draw_tesselations:
            for face_landmarks in face_landmarks_list:
                face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                face_landmarks_proto.landmark.extend([
                    landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z)
                    for landmark in face_landmarks])
                solutions.drawing_utils.draw_landmarks(
                    image=annotated_image,
                    landmark_list=face_landmarks_proto,
                    connections=solutions.face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.draw_spec_tesselation
                )

        return annotated_image

    def draw_points(self, df, image, draw_options: DrawOptions,
                    node_injections_df=None, region_injections_df=None, node_regions_df=None):
        required_columns = {'x', 'y', 'point'}
        if not required_columns.issubset(df.columns) or df.empty:
            return

        x_points = df['x'].astype(int)
        y_points = df['y'].astype(int)
        point_labels = df['point']
        injection_labels = df.get('treatment_type', None)
        region_names = df.get('name', None)
        displayed_regions = set()

        for i in range(len(df)):
            x_point, y_point = x_points.iloc[i], y_points.iloc[i]
            point_label = point_labels.iloc[i]
            label_to_draw = ""

            # injection labels
            if draw_options.draw_all_injections and injection_labels is not None and pd.notna(injection_labels.iloc[i]):
                injection_label = injection_labels.iloc[i]
                if node_injections_df is not None and not node_injections_df.empty:
                    relevant_ids = node_injections_df[node_injections_df['node_id'] == point_label]['injection_id']
                    if not relevant_ids.empty:
                        matching_labels = df[df['id'].isin(relevant_ids)]['name'].drop_duplicates()
                        if not matching_labels.empty:
                            label_to_draw = f"{injection_label.title()} ({', '.join(matching_labels.astype(str))})"
                        else:
                            label_to_draw = f"{injection_label.title()}"

            # text modifier for injection label
            if label_to_draw:
                injection_text_mod = self.landmark_injection_text_mod
                injection_text_mod.draw_point(annotated_image=image, point_x=x_point, point_y=y_point,
                                              label=label_to_draw)
                continue

            # region names
            region_label = ""
            if region_names is not None and pd.notna(region_names.iloc[i]):
                region_name = region_names.iloc[i]
                if node_regions_df is not None and not node_regions_df.empty:
                    relevant_regions = node_regions_df[node_regions_df['point'] == point_label][
                        'name'].drop_duplicates()
                    if not relevant_regions.empty:
                        region_name = f"{region_name.title()} ({', '.join(relevant_regions.astype(str))})"

                if region_name not in displayed_regions:
                    displayed_regions.add(region_name)
                    region_label = f" {region_name.title()}"

            # Determine text modifier for region label
            if region_label:
                landmark_text_mod = self.landmark_label_text_mod
                landmark_text_mod.draw_point(annotated_image=image, point_x=x_point, point_y=y_point,
                                             label=region_label.strip().title())

    def project_polygons(self, frame, height, width, face_landmarks_list, filtered_df=None, regions_to_plot=None,
                         draw_options: DrawOptions = None):
        def parse(value):
            return normalize_string(value).lower() if isinstance(value, str) else value

        detected_landmarks = {k: v for face_landmark in face_landmarks_list for k, v in face_landmark.items()}
        sub_mapping_df = self.mapped_nodes_df.copy()
        sub_mapping_df['name'] = sub_mapping_df['name'].apply(parse)

        if filtered_df is not None and not filtered_df.empty:
            filtered_df['name'] = filtered_df['name'].apply(parse)
            sub_mapping_df = sub_mapping_df[sub_mapping_df['name'].isin(filtered_df['name'])]

        if draw_options and draw_options.draw_all_regions:
            regions_to_plot = [parse(region) for region in self.regions_df['name']]
        elif regions_to_plot:
            regions_to_plot = [parse(region) for region in regions_to_plot]
            sub_mapping_df = sub_mapping_df[sub_mapping_df['name'].isin(regions_to_plot)]
        else:
            sub_mapping_df = sub_mapping_df[[]]  # Empty DataFrame if no regions to plot

        if sub_mapping_df.empty:
            return frame

        num_groups = len(sub_mapping_df)
        colors = [(int(c[0] * 255), int(c[1] * 255), int(c[2] * 255))
                  for c in cm.rainbow(np.linspace(0, 1, num_groups))[:, :3]]

        for group_idx, (_, row) in enumerate(sub_mapping_df.iterrows()):
            mapped_landmarks = [detected_landmarks.get(label) for label in row['landmark'] if
                                label in detected_landmarks]

            if len(mapped_landmarks) < 2:
                continue

            df_landmarks = np.array(row['landmark_coords'])[:, :2]
            mp_landmarks = np.array(mapped_landmarks)[:, :2]

            centroids_df = df_landmarks.mean(axis=0)
            centroid_mp = mp_landmarks.mean(axis=0)

            range_x_df = df_landmarks[:, 0].max() - df_landmarks[:, 0].min()
            range_y_df = df_landmarks[:, 1].max() - df_landmarks[:, 1].min()
            range_x_mp = mp_landmarks[:, 0].max() - mp_landmarks[:, 0].min()
            range_y_mp = mp_landmarks[:, 1].max() - mp_landmarks[:, 1].min()

            scale_x = range_x_mp / range_x_df if range_x_df > 0 else 1.0
            scale_y = range_y_mp / range_y_df if range_y_df > 0 else 1.0

            for polygon in row['segmentation']:
                polygon_points = np.array(polygon).reshape(-1, 2)
                translated_polygon = polygon_points - centroids_df
                scaled_polygon = translated_polygon * [scale_x, scale_y]
                polygon_scaled = scaled_polygon + centroid_mp

                polygon_scaled_int = np.array(
                    [[int(x * width), int(y * height)] for x, y in polygon_scaled],
                    dtype=np.int32
                )

                cv2.polylines(frame, [polygon_scaled_int], isClosed=True, color=colors[group_idx], thickness=2)
                overlay = frame.copy()
                cv2.fillPoly(overlay, [polygon_scaled_int], color=colors[group_idx])
                cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)

        return frame

    def detect_on_image_proto(self, image_path, drawing_options=None, st_frame=None):
        draw_options = DrawOptions() if drawing_options is None else drawing_options

        img_cv = cv2.imread(image_path)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(img_cv,cv2.COLOR_BGR2RGB))
        height, width, _ = img_cv.shape

        annotated_image = self.detect_and_draw(frame=image, width=width, height=height, draw_options=draw_options)

        if st_frame is not None:
            st_frame.image(annotated_image, use_container_width=True)
        else:
            cv2.imshow("image", cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB))

        cv2.waitKey(0)
        cv2.destroyAllWindows()


    def detect_on_stream_proto(self, drawing_options=None, st_frame=None):
        draw_options = DrawOptions() if drawing_options is None else drawing_options
        camera = cv2.VideoCapture(0)

        while camera.isOpened():
            ret, frame = camera.read()
            if not ret:
                return camera.release()

            frame = cv2.flip(frame, 1)
            width, height, _ = frame.shape
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

            annotated_image = self.detect_and_draw(width, height, frame=image, draw_options=draw_options)

            if st_frame is not None:
                st_frame.image(cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB), use_container_width=True)
            else:
                cv2.imshow('annotated_frame', annotated_image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break


def log(message, *args):
    print(f"\n----[ARBotox @ DataDriver]: {message} {args}")
