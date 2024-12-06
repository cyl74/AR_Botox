#import src.vision.AnatomyMap
from src.archive import Landmarker
#from src.vision import AnatomyMap
import db_api.db as db
#import src.vision.ArBotox as ArBotox

from src.vision.ArBotox import ArBotox, DrawOptions

OUTPUT_LANDMARK_CSV = "data/outputs/landmarks.csv"

WOMAN_1 = "res/woman1.jpg"
WOMAN_2 = "res/woman2.jpg"
WOMAN_3 = "res/woman3.png"

FACE_ANATOMY = "res/anatomy_face.png"
FACE_BLUR_IMG = "res/img2.png"

"""
You can specify ranges for detect_on_image if you want to only view specific landmark labels here
"""
START_RANGE = 100
END_RANGE = 115

def main():
    face_landmarker = Landmarker.Landmarker()
  #  anatomy_map = AnatomyMap.AnatomyMap()

    """
    .....Test some detections on screen here. Pick one. Modify some parameters here......
    - If landmarks aren't showing, it means detector could not detect a face. Change the image.
    - If you're getting error on MP not reading an image, you can try to adjust loading img between: cv2.imread and mp.Image.create_from_file
    - If your stream is lagging, set parameter 'export_csv=False' 
    - Each image detection outputs .csv and .png; each stream detection outputs .csv. you can view results in data/outputs
    """
    #face_landmarker.detect_range_on_image(image_path='res/img.png', landmark_range=(START_RANGE,END_RANGE), draw_tesselations=True, draw_labels=True, export_csv=True)
    #face_landmarker.detect_on_image(image_path=FACE_BLUR_IMG, draw_tesselations=True, draw_labels=False, export_csv=True)
    #face_landmarker.detect_all_on_stream(draw_tesselations=True, draw_labels=True,  export_csv=True)
    #face_landmarker.detect_region_on_stream(regions=[anatomy_map.LIPS, anatomy_map.LEFT_EYE], draw_injections=True,draw_tesselations=True,draw_labels=True, draw_start_end=False,  export_csv=True)

    # ---> For segmenting regions from images - archive functions, might not use
    #segmented_masks = AnatomyMapper().segment_image(MARKED_FACE)
    #region = AnatomyMapper().find_landmarks_in_region(TRAIN_IMG, MASK_IMG)
    #print(region.__dict__)


    # 1. Initialize here.
    # Load data base only once, then set to False
    arBotox = ArBotox(reload_data_to_database=False)

    draw_options = DrawOptions(
        regions=['Orbital Oculi','Columella','Buccinator','Levator Labii Superioris','Nose Tip','masseter','frontalis'],
        treatment_type=['Bunny Lines', "crow's feet"],
        draw_all_injections=True,
        draw_tesselations=False,
        draw_all_regions=True
    )

    arBotox.detect_on_image_proto(WOMAN_1, draw_options)
    #arBotox.detect_on_stream_proto(draw_options)


if __name__ == '__main__':
    main()
