from mediapipe import solutions
import cv2


class TextModifier:

    # Font's fill size and border size. Ajust font sizes first.
    FONT_FILL_SIZE = .3
    FONT_FILL_THICKNESS = 1
    FONT_BORDER_SIZE = .3
    FONT_BORDER_THICKNESS = 3
    FONT_FILL_COLOUR = (255, 255, 255)
    FONT_BORDER_COLOUR = (0, 0, 0)

    # Landmarker Mods
    LANDMARKER_FILL_COLOUR =  (255,255,255)
    LANDMARKER_BORDER_COLOUR =  (255,255,255)
    LANDMARKER_RADIUS = 3

    # Drawing specs for Landmarker - Ignore
    draw_spec_point = solutions.drawing_utils.DrawingSpec()
    draw_spec_point.color = (255, 255, 255)
    draw_spec_point.thickness = 1
    draw_spec_point.circle_radius = 1
    draw_spec_tesselation = solutions.drawing_utils.DrawingSpec()
    draw_spec_tesselation.color = (180, 180, 180)
    draw_spec_tesselation.thickness = 1

    def set_default_small(self):
        self.FONT_FILL_SIZE = .3
        self.FONT_FILL_THICKNESS = 1
        self.FONT_BORDER_SIZE = .3
        self.FONT_BORDER_THICKNESS = 3
        FONT_FILL_COLOUR=(0, 0, 0),
        FONT_BORDER_COLOUR=(0, 0, 0)

        # Landmarker Mods
        self.LANDMARKER_FILL_COLOUR = (255,255,255)
        self.LANDMARKER_RADIUS = 5

    def set_default_large(self): # For larger frames
        self.FONT_FILL_SIZE = .6
        self.FONT_FILL_THICKNESS = 1
        self.FONT_BORDER_SIZE = .6
        self.FONT_BORDER_THICKNESS = 3
        FONT_FILL_COLOUR=(0, 0, 0),
        FONT_BORDER_COLOUR=(0, 0, 0)
        # Landmarker Mods
        self.LANDMARKER_FILL_COLOUR =  (255,255,255)
        self.LANDMARKER_RADIUS = 3

    """
    Overrides all default settings, you can modify your own customs with this
    """
    def set_custom_mods(self,
            FONT_FILL_SIZE = FONT_FILL_SIZE,
            FONT_FILL_THICKNESS = FONT_FILL_THICKNESS,
            FONT_BORDER_SIZE = FONT_BORDER_SIZE,
            FONT_BORDER_THICKNESS = FONT_BORDER_THICKNESS,
            FONT_FILL_COLOUR = FONT_FILL_COLOUR,
            FONT_BORDER_COLOUR = FONT_BORDER_COLOUR,
            LANDMARKER_FILL_COLOUR = LANDMARKER_FILL_COLOUR,
            LANDMARKER_BORDER_COLOUR = LANDMARKER_BORDER_COLOUR,
            LANDMARKER_RADIUS = LANDMARKER_RADIUS):
        self.FONT_FILL_SIZE = FONT_FILL_SIZE
        self.FONT_FILL_THICKNESS = FONT_FILL_THICKNESS
        self.FONT_BORDER_SIZE = FONT_BORDER_SIZE
        self.FONT_BORDER_THICKNESS = FONT_BORDER_THICKNESS
        self.FONT_FILL_COLOUR = FONT_FILL_COLOUR
        self.FONT_BORDER_COLOUR = FONT_BORDER_COLOUR
        # Landmarker Mods
        self.LANDMARKER_FILL_COLOUR = LANDMARKER_FILL_COLOUR
        self.LANDMARKER_BORDER_COLOUR = LANDMARKER_BORDER_COLOUR
        self.LANDMARKER_RADIUS = LANDMARKER_RADIUS

    # Draws fancy text with innerfill and outerborder text
    def draw_point(self, annotated_image, point_x, point_y, label=None):
        cv2.circle(annotated_image, (point_x, point_y), self.LANDMARKER_RADIUS, self.LANDMARKER_FILL_COLOUR, -1)
        cv2.circle(annotated_image, (point_x, point_y), self.LANDMARKER_RADIUS, self.LANDMARKER_BORDER_COLOUR, -1)
        if label is not None:
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_COMPLEX, self.FONT_FILL_SIZE, self.FONT_FILL_THICKNESS)[
                0]
            text_width, text_height = text_size[0], text_size[1]
            text_x = point_x + self.LANDMARKER_RADIUS + 5
            text_y = point_y - self.LANDMARKER_RADIUS - 5
            text_x = max(text_x, 0)
            text_y = max(text_y, text_height)
            # BORDER MOD
            cv2.putText(img=annotated_image, text=label, org=(text_x, text_y),
                        fontFace=cv2.FONT_HERSHEY_COMPLEX,
                        fontScale=self.FONT_BORDER_SIZE,
                        color=self.FONT_BORDER_COLOUR,
                        thickness=self.FONT_BORDER_THICKNESS, lineType=cv2.LINE_AA)
            # FILL MOD
            cv2.putText(img=annotated_image, text=label, org=(text_x, text_y),
                        fontFace=cv2.FONT_HERSHEY_COMPLEX,
                        fontScale=self.FONT_FILL_SIZE,
                        color=self.FONT_FILL_COLOUR,
                        thickness=self.FONT_FILL_THICKNESS, lineType=cv2.LINE_AA)


"""
You can modify text/plotting visuals here for the points and labels !.
"""

#' START' marker
landmark_start_text_mod = TextModifier()
landmark_start_text_mod.set_custom_mods(
        FONT_FILL_COLOUR=(0,255,0),
        FONT_FILL_SIZE=TextModifier.FONT_FILL_SIZE*1,
        FONT_FILL_THICKNESS=TextModifier.FONT_FILL_THICKNESS*1,
        FONT_BORDER_SIZE=TextModifier.FONT_BORDER_SIZE*1,
        FONT_BORDER_THICKNESS=TextModifier.FONT_BORDER_THICKNESS*3)

# 'END' marker
landmark_end_text_mod = TextModifier()
landmark_end_text_mod.set_custom_mods(
        FONT_FILL_COLOUR=(108, 178, 240),
        FONT_FILL_SIZE=TextModifier.FONT_FILL_SIZE*1,
        FONT_FILL_THICKNESS=TextModifier.FONT_FILL_THICKNESS*1,
        FONT_BORDER_SIZE=TextModifier.FONT_BORDER_SIZE*1,
        FONT_BORDER_THICKNESS=TextModifier.FONT_BORDER_THICKNESS*3,)

"""
Default landmarking
"""
landmark_point_text_mod = TextModifier()
landmark_point_text_mod.set_default_small()

# Injection Points
landmark_injection_text_mod = TextModifier()
landmark_injection_text_mod.set_custom_mods(
        FONT_FILL_SIZE=TextModifier.FONT_FILL_SIZE*1,
        FONT_FILL_THICKNESS=TextModifier.FONT_FILL_THICKNESS*1,
        FONT_BORDER_SIZE=TextModifier.FONT_BORDER_SIZE*1,
        FONT_BORDER_THICKNESS=TextModifier.FONT_BORDER_THICKNESS*1,
        FONT_FILL_COLOUR=(108, 178, 240),
        FONT_BORDER_COLOUR=(0, 0, 0),
        LANDMARKER_FILL_COLOUR=(255, 0, 0),
        LANDMARKER_BORDER_COLOUR=(255, 0, 0),
        LANDMARKER_RADIUS=TextModifier.LANDMARKER_RADIUS*2)
