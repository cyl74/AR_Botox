import csv
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks.python.vision import FaceLandmarker
import numpy as np
import cv2
import src.utils.TextModifier as TextModifier
import time

class FaceLandmarker:
    mediapipe_base_options = None
    face_landmarker = None
    face_landmarker_options = None
    base_options = None
    options = None
    detector = None

    def __init__(self, num_faces=1, min_detection_confidence=0.6, min_track_confidence=0.6,):
        self.mediapipe_base_options = mp.tasks.BaseOptions
        self.face_landmarker = mp.tasks.vision.FaceLandmarker
        self.face_landmarker_options = mp.tasks.vision.FaceLandmarkerOptions
        self.base_options = BaseOptions(model_asset_path='task/face_landmarker.task')
        self.options = FaceLandmarkerOptions(base_options=base_options,
                                        output_face_blendshapes=True,
                                        output_facial_transformation_matrixes=True,
                                        num_faces=num_faces,
                                        min_face_detection_confidence=min_detection_confidence,
                                        min_tracking_confidence=min_track_confidence)
        self.detector = FaceLandmarker.create_from_options(self.Options)


class Landmarker:
    BaseOptions = mp.tasks.BaseOptions
    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
    base_options = BaseOptions(model_asset_path='task/face_landmarker.task')
    options = FaceLandmarkerOptions(base_options=base_options,
                                    output_face_blendshapes=True,
                                    output_facial_transformation_matrixes=True,
                                    num_faces=1,
                                    min_face_detection_confidence=.6,
                                    min_tracking_confidence=.6)
    detector = FaceLandmarker.create_from_options(options)
    CSV_HEADER = ["point", "landmark.x", "landmark.y", "landmark.z", "timestamp"]

    landmark_label_text_mod = TextModifier.landmark_point_text_mod
    landmark_start_text_mod = TextModifier.landmark_start_text_mod
    landmark_end_text_mod = TextModifier.landmark_end_text_mod
    landmark_injection_text_mod = TextModifier.landmark_injection_text_mod
    draw_spec_tesselation = TextModifier.TextModifier.draw_spec_tesselation



    # ----- DRAWING -----
    """
    ----- DRAWER: DRAW REGIONAL DETECTED LANDMARKS -----
    This function takes in an image/frame and detects landmarks if a face is detected.
    Modificated draw by drawing points only by Region with optional injections and start/end nodes.
    """
    def draw_landmarks_in_region(self, frame, detection_result,
                                 regions,
                                 draw_injections=True,
                                 draw_tesselations=True,
                                 draw_labels=False,
                                 draw_start_end=False,
                                 csvfile=None):
        face_landmarks_list = detection_result.face_landmarks
        annotated_image = np.copy(frame)

        for idx in range(len(face_landmarks_list)):
            face_landmarks = face_landmarks_list[idx]
            face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            face_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in face_landmarks
            ])
            if draw_tesselations:
                solutions.drawing_utils.draw_landmarks(
                    image=annotated_image,
                    landmark_list=face_landmarks_proto,
                    connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.draw_spec_tesselation)

            for point, landmark in enumerate(face_landmarks):
                height, width, _ = annotated_image.shape
                point_x = int(landmark.x * width)
                point_y = int(landmark.y * height)
                if csvfile is not None:
                    with open(csvfile, 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([point, landmark.x, landmark.y, landmark.z, time.time_ns()])
                for region in regions:
                    if point in region.nodes:
                        #   DRAW INJECTIONS
                        if draw_injections and region.injection_points is not None and point in region.injection_points:
                            self.landmark_injection_text_mod.draw_point(annotated_image=annotated_image,point_x=point_x,point_y=point_y,label="INJECTION POINT")
                        elif draw_start_end is True:
                            # DRAW MARKER START
                            if point == region.connections[0].start:
                                self.landmark_start_text_mod.draw_point(annotated_image=annotated_image,point_x=point_x,point_y=point_y,label="START")
                            # DRAW MARKER END
                            elif point == region.connections[0].end:
                                self.landmark_end_text_mod.draw_point(annotated_image=annotated_image,point_x=point_x,point_y=point_y,label="END")

                        else:
                            # DRAW ALL OTHER NODES (IN REGION)
                            if draw_labels:
                                self.landmark_label_text_mod.draw_point(annotated_image=annotated_image,point_x=point_x,point_y=point_y,label=str(point))
                            else:
                                self.landmark_label_text_mod.draw_point(annotated_image=annotated_image,
                                                                        point_x=point_x, point_y=point_y,
                                                                        label=None)

        return annotated_image


    """
    ----- DRAWER: DRAW RANGE IN LANDMARKS -----
    This function takes in an image/frame and detects landmarks if a face is detected.
    Modificated draw by drawing points only in the range of points given.
    """

    def draw_landmarks_in_range(self, image,
                                datection_result,
                                landmark_range,
                                draw_tesselations=True,
                                draw_labels=True,
                                csvfile=None):

        face_landmarks_list = datection_result.face_landmarks
        annotated_image = np.copy(image)

        for idx in range(len(face_landmarks_list)):
            face_landmarks = face_landmarks_list[idx]
            face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            face_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in face_landmarks])

            if draw_tesselations:
                solutions.drawing_utils.draw_landmarks(
                    image=annotated_image,
                    landmark_list=face_landmarks_proto,
                    connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.draw_spec_tesselation)


            for point, landmark in enumerate(face_landmarks):
                if landmark_range[0] <= point <= landmark_range[1]:
                    height, width, _ = annotated_image.shape
                    point_x = int(landmark.x * width)
                    point_y = int(landmark.y * height)
                    if csvfile is not None:
                        with open(csvfile, 'a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow([point, landmark.x, landmark.y, landmark.z, time.time_ns()])
                    if draw_labels:
                        self.landmark_label_text_mod.draw_point(annotated_image=annotated_image,point_x=point_x,point_y=point_y,label=str(point))
                    else:
                        self.landmark_label_text_mod.draw_point(annotated_image=annotated_image,
                                                                point_x=point_x, point_y=point_y,
                                                                label=None)

        return annotated_image

    """
    ----- DRAWER: DRAW ALL DETECTED LANDMARKS -----
    This function takes in a given image or frame and detects landmarks if a face is detected.
    It then draws the points and labels on the image with the detected landmark points.
    """
    def draw_all_landmarks(self, frame, detection_result,
                           draw_tesselations=True,
                           draw_labels=False,
                           csvfile=None):

        face_landmarks_list = detection_result.face_landmarks
        annotated_image = np.copy(frame)

        for idx in range(len(face_landmarks_list)):
            face_landmarks = face_landmarks_list[idx]
            face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            face_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in face_landmarks
            ])

            if draw_tesselations:
                solutions.drawing_utils.draw_landmarks(
                    image=annotated_image,
                    landmark_list=face_landmarks_proto,
                    connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.draw_spec_tesselation)
            # DRAW ALL NODES
            for point, landmark in enumerate(face_landmarks):
                if csvfile is not None:
                    with open(csvfile, 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([point, landmark.x, landmark.y, landmark.z, time.time_ns()])

                height, width, _ = annotated_image.shape
                point_x = int(landmark.x * width)
                point_y = int(landmark.y * height)
                if draw_labels is False:
                    self.landmark_label_text_mod.draw_point(annotated_image=annotated_image, point_x=point_x, point_y=point_y)
                else:
                    self.landmark_label_text_mod.draw_point(annotated_image=annotated_image, point_x=point_x, point_y=point_y, label=str(point))

        return annotated_image


    # ----- UTILIITY -----
    """
    For creating regions via image input using a segmented mask from kmeans. >> Need to modify
        def detect_region_on_image(self, image_path, regions, segment_mask, region_name):
        anatomy_mapper = AnatomyMapper()
        base_options = python.BaseOptions(model_asset_path='task/face_landmarker.task')
        options = vision.FaceLandmarkerOptions(base_options=base_options,
                                               output_face_blendshapes=True,
                                               output_facial_transformation_matrixes=True,
                                               num_faces=1)
        detector = vision.FaceLandmarker.create_from_options(options)
        image = mp.Image.create_from_file(image_path)
        detection_result = detector.detect(image)
        region = anatomy_mapper.find_landmarks_in_region(image_path.numpy_view(),
                                                         detection_result,
                                                         regions=None,
                                                         segment= segment_mask,
                                                         region_name="NAME")
    """

    # ------ VIEWING MODES ------

    """
    ----- VIEWING: DETECT LANDMARK POINTS ON AN IMAGE -----
    For viewing landmarks on images.
    """
    def detect_on_image(self, image_path,
                        draw_tesselations=True,
                        draw_labels=True,
                        export_csv=True):

        csvfile = f"data/outputs/landmarks_image_all_{time.time()}.csv"
        img_cv = cv2.imread(image_path)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_cv)
        #image = mp.Image.create_from_file(image_path)
        if export_csv is True:
            with open(csvfile, 'w', newline='') as file:
                writer = csv.writer(file)
                header = self.CSV_HEADER
                writer.writerow(header)
        detection_result = self.detector.detect(image)
        annotated_image = self.draw_all_landmarks(image.numpy_view(), detection_result,
                                                  draw_tesselations=draw_tesselations,
                                                  draw_labels=draw_labels,
                                                  csvfile=csvfile)
        cv2.imshow("image", cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB))
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.imwrite(f"data/outputs/landmarks_image_all_{time.time()}.png", cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB))

    """
        ----- VIEWING: DETECT LANDMARK RANGE ON AN IMAGE -----
        For viewing landmarks only with the specified range on images.
        Input a (start, end) tuple. (Not to be confused with draw-regions
        """

    def detect_range_on_image(self, image_path,
                              landmark_range,
                              draw_tesselations=True,
                              draw_labels=False,
                              export_csv=True):
        img_cv = cv2.imread(image_path)
        image = mp.Image.create_from_file(image_path)
      #  image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_cv)
        csvfile = None
        if export_csv is True:
            csvfile = f"data/outputs/landmarks_image_range_{landmark_range[0]}_{landmark_range[1]}_{time.time()}.csv"
            with open(csvfile, 'w', newline='') as file:
                writer = csv.writer(file)
                header = self.CSV_HEADER
                writer.writerow(header)
        detection_result = self.detector.detect(image)
        annotated_image = self.draw_landmarks_in_range(image=image.numpy_view(),
                                                       datection_result=detection_result,
                                                        landmark_range=landmark_range,
                                                        draw_tesselations=draw_tesselations,
                                                        draw_labels=draw_labels,
                                                        csvfile=csvfile)
        cv2.imshow("image", cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB))
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.imwrite(f"data/outputs/landmarks_image_range_{landmark_range[0]}_{landmark_range[1]}_{time.time()}.png",
                    cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB))

    """
     ----- VIEWING: DETECT LANDMARK POINTS OF A REGION ON CAMERA STREAM -----
    Show only regions of landmark points on webcam.
    Region parameter should be a list[Anatomy.Region]
    """
    def detect_region_on_stream(self, regions,
                                draw_injections=True,
                                draw_tesselations=True,
                                draw_labels=False,
                                draw_start_end=False,
                                export_csv=True):
        camera = cv2.VideoCapture(0)
        csvfile = None
        if export_csv is True:
            csvfile = f"data/outputs/landmarks_stream_regions_{'_and_'.join([region.name for region in regions])}_{time.time()}.csv"
            with open(csvfile, 'w', newline='') as file:
                writer = csv.writer(file)
                header = self.CSV_HEADER
                writer.writerow(header)
        while camera.isOpened():
            ret, frame = camera.read()
            if not ret:
                return camera.release()
            frame = cv2.flip(frame, 1)
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            detection_result = self.detector.detect(image)
            timestamp = time.time_ns()
            annotated_image = self.draw_landmarks_in_region(image.numpy_view(), detection_result,
                                                            regions=regions,
                                                            draw_injections=draw_injections,
                                                            draw_tesselations=draw_tesselations,
                                                            draw_labels=draw_labels,
                                                            draw_start_end=draw_start_end,
                                                            csvfile=csvfile)
            cv2.imshow('annotated_frame', annotated_image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

    """
    ----- VIEWING: DETECT ALL LANDMARK POINTS ON A CAMERA STREAM -----
    Show all landmark points in the webcam.
    """
    def detect_all_on_stream(self, draw_tesselations=True,
                             draw_labels=False,
                             export_csv=True):
        camera = cv2.VideoCapture(0)

        csvfile = None
        if export_csv is True:
            csvfile = f"data/outputs/landmarks_stream_all_{time.time()}.csv"
            with open(csvfile, 'w', newline='') as file:
                writer = csv.writer(file)
                header = self.CSV_HEADER
                writer.writerow(header)
        while camera.isOpened():
            ret, frame = camera.read()
            if not ret:
                return camera.release()
            frame = cv2.flip(frame, 1)
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            detection_result = self.detector.detect(image)
            annotated_image = self.draw_all_landmarks(image.numpy_view(), detection_result,
                                                      draw_tesselations=draw_tesselations,
                                                      draw_labels=draw_labels,
                                                      csvfile=csvfile)

            cv2.imshow('annotated_frame', annotated_image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break