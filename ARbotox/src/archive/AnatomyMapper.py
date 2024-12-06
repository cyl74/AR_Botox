
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import face_landmarker, FaceLandmarker
import numpy as np
import matplotlib.pyplot as plt
import cv2
import src.archive.AnatomyMap as AnatomyMap


class AnatomyMapper:
    detector = None
    def __init__(self):

        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = mp.tasks.vision.FaceLandmarker
        FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
        base_options = BaseOptions(model_asset_path='task/face_landmarker.task')
        options = FaceLandmarkerOptions(base_options=base_options,
                                        output_face_blendshapes=True,
                                        output_facial_transformation_matrixes=True,
                                        num_faces=1, )
        self.detector = FaceLandmarker.create_from_options(options)

    def check_valid(self, valid_x, valid_y, mask_grid):
        valid = (valid_x < mask_grid.shape[0]) & (valid_y < mask_grid.shape[1])
        valid_x = valid_x[valid]
        valid_y = valid_y[valid]
        return np.any(mask_grid[valid_x, valid_y] == 1)

    """
    Process the segmented image from kmeans - only look at pixels where value > 0, indicating coloured pixel.
    Coloured pixels indicate being part of the region of interest. Next create masks.
    mask_grid : create a binary (0-1) grid for the segmented image.
    mask_frame : the painted visual of the segmented 2D equivalent to points on the mask_rid
    """
    def create_masks(self, frame, segmented_image):
        # Obtain the coordinates for the points of interest in the segmented 2D image extraction,
        # where points of interest are values greater than 0, indicating a coloured pixel.
        segmented_image = cv2.resize(segmented_image, (frame.shape[1], frame.shape[0]),
                                       interpolation=cv2.INTER_AREA)
        segmented_sifted_points = np.where(segmented_image > 0)
        height, width, _ = frame.shape
        mask_frame = np.zeros_like(frame)  # one mask to paint segmented area on frame
        mask_grid_frame = np.zeros_like(frame)

        for i in range(0, len(segmented_sifted_points[0])):
            sy = int(segmented_sifted_points[0][i])
            sx = int(segmented_sifted_points[1][i])  # correct ratio due to reshaping

            # ensure that the points from the isolation image fall within the boundary for the camera frame.
            if sx < width and sy < height:
                cv2.circle(mask_frame, (sx, sy), 2, (255), -1)
                mask_grid_frame[sy, sx] = 1

        return mask_grid_frame, mask_frame


    """
    Find any nodes that fall in the segmented image.
    segmented_image : the mask which is to extract nodes within.
    Note -> returned list is not cleaned, may have anomalies.
    """
    def process_and_detect(self, image, segmented_image):
        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = mp.tasks.vision.FaceLandmarker
        FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
        base_options = BaseOptions(model_asset_path='task/face_landmarker.task')
        options = FaceLandmarkerOptions(base_options=base_options,
                                        output_face_blendshapes=True,
                                        output_facial_transformation_matrixes=True,
                                        num_faces=1, )
        detector = vision.FaceLandmarker.create_from_options(options)

        mask_image = cv2.imread(segmented_image)
        segmented_image = mask_image.reshape(mask_image.shape[0], mask_image.shape[1] * mask_image.shape[2])

        image = mp.Image.create_from_file(image)
        detection_result = detector.detect(image)

        return image.numpy_view(), detection_result, segmented_image


    """
    Given an segmented image, create a new Region object from the input image and segmented image.
    Return the computed coordinates of the nodes that correspond with the location of the cooordinates of the input image.
    """
    def find_landmarks_in_region(self, image, segmented_image, region_name = None, thresh_x=4, thresh_y=4):

        image, detection_result, segmented_image = self.process_and_detect(image, segmented_image)
        mask_grid, mask_frame = self.create_masks(image, segmented_image)

        discovered_nodes = [] # to record the nodes falling in the region of interest
        region = AnatomyMap.Region()
        face_landmarks_list = detection_result.face_landmarks
        for idx in range(len(face_landmarks_list)):
            face_landmarks = face_landmarks_list[idx]
            face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            face_landmarks_proto.landmark.extend( [landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in face_landmarks])

            for point, landmark in enumerate(face_landmarks):
                height, width, _ = image.shape
                point_x = int(landmark.x * width)
                point_y = int(landmark.y * height)

                # Creating the "acceptable" range of x and ys
                range_x = range(point_x - thresh_x, point_x + thresh_x + 1)
                range_y = range(point_y - thresh_y, point_y + thresh_y + 1)
                px, py = np.meshgrid(range_y, range_x, indexing='ij')
                valid = (py < width) & (px < height) & (point_x < width) & (point_y < height)
                valid_px = px[valid]
                valid_py = py[valid]

                if self.check_valid(valid_px, valid_py, mask_grid):
                    node = AnatomyMap.Node(point)
                    discovered_nodes.append(node)

        if region_name is not None:
            region.name = region_name
        region.nodes = discovered_nodes
        return region

    def plot_masks(self, masks):
        n = len(masks)-1
        fig, axes = plt.subplots(1, n, figsize=(20, 10))
        for i in range(n):
            axes[i].imshow(cv2.cvtColor(segmented_image, cv2.COLOR_BGR2RGB))
            axes[i].set_title(f'Cluster {i}')
            axes[i].axis('off')
        plt.show()

    def segment_image(self, image_path):
        image = cv2.imread(image_path)
        image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        masks = []

        contrast = 1
        brightness = 0
        image = cv2.addWeighted(image, contrast, np.zeros(image.shape, image.dtype), 0, brightness)
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        image = cv2.filter2D(image, -1, kernel)

        """
        Vectorize the image for k-means. Flatten each pixel's RGB values into a single vector [R,G,B].
        Reshape the image from a 2D array to a 1D array of vectors.
        After clustering, apply centroid values to all pixels such that resulting image will have specified number of colours.
        Reshape it back to the original image.
        """

        Z = image.reshape((-1, 3))
        Z = np.float32(Z)

        # Define k-means parameters
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        K = 15
        attempts = 10

        ret, label, center = cv2.kmeans(Z, K, None, criteria, attempts, cv2.KMEANS_PP_CENTERS)

        # Convert center to uint8 (color values) and reshape
        center = np.uint8(center)
        res = center[label.flatten()]
        # This image has the segment colours
        result_image = res.reshape((image.shape))

        for i in range(K):
            mask = (label == i).reshape(result_image.shape[:2])  # Create a mask for cluster i
            segmented_image = np.zeros_like(result_image)  # Create an empty image to store this cluster's section
            segmented_image[mask] = result_image[mask]  # Apply the mask to isolate this cluster
            cv2.imwrite("mask_%d.png" % i, segmented_image)
            masks.append(segmented_image)

        return masks