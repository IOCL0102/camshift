import cv2
import numpy as np
import util
from util import COLOR
from util import TERMINAL_TEXT_COLOR as ttc


class ROI_SELECTOR_PARAMS:
    frame: list = None
    frame_width: int = None
    frame_height: int = None

    cursor_position: tuple = None
    box_start_position: tuple = None
    box_end_position: tuple = None
    is_update_required: bool = False
    is_tracking: bool = False

    _left_btn_up_clicked: bool = False
    _is_cursor_moving: bool = False

    @staticmethod
    def attach_frame(frame):
        ROI_SELECTOR_PARAMS.frame = frame
        ROI_SELECTOR_PARAMS.frame_width = np.asarray(frame).shape[1]
        ROI_SELECTOR_PARAMS.frame_height = np.asarray(frame).shape[0]

    @staticmethod
    def show_ROI_box(mask, box_stroke_color=COLOR.GREEN_BGR):
        if not isinstance(box_stroke_color, COLOR):
            ttc.warning("box_stroke_color is not instance of COLOR Enum class")
            return

        if ROI_SELECTOR_PARAMS._is_cursor_moving:
            cv2.rectangle(
                mask, ROI_SELECTOR_PARAMS.box_start_position, ROI_SELECTOR_PARAMS.box_end_position, box_stroke_color.value, 2)

    @staticmethod
    def show_coordinate(frame, text_color=COLOR.RED_BGR, normalized=False, normalized_max=100):
        if not isinstance(text_color, COLOR):
            ttc.warning("text_color is not instance of COLOR Enum class")
            return

        if ROI_SELECTOR_PARAMS.cursor_position == None \
                or ROI_SELECTOR_PARAMS.cursor_position[0] == None \
                or ROI_SELECTOR_PARAMS.cursor_position[1] == None:
            return

        # x and y value
        x = y = 0.0

        # x and y position value
        text_x_pos = text_y_pos = 0.0

        if normalized is True:
            coordinate = ROI_SELECTOR_PARAMS.get_normalized_coordinate()
            x = coordinate[0]*normalized_max
            y = coordinate[1]*normalized_max
        else:
            x = ROI_SELECTOR_PARAMS.cursor_position[0]
            y = ROI_SELECTOR_PARAMS.cursor_position[1]

        frame_width = ROI_SELECTOR_PARAMS.frame_width
        frame_height = ROI_SELECTOR_PARAMS.frame_height
        boundary_x = frame_width/5
        boundary_y = frame_height/5

        if ROI_SELECTOR_PARAMS.cursor_position[0] < frame_width-boundary_x:
            text_x_pos = int(ROI_SELECTOR_PARAMS.cursor_position[0]+10)
        else:
            text_x_pos = int(
                ROI_SELECTOR_PARAMS.cursor_position[0]-boundary_x*1.5)

        if ROI_SELECTOR_PARAMS.cursor_position[1] > boundary_y:
            text_y_pos = int(ROI_SELECTOR_PARAMS.cursor_position[1]-10)
        else:
            text_y_pos = int(
                ROI_SELECTOR_PARAMS.cursor_position[1]+boundary_y*0.2)

        cv2.putText(frame, f"({float(x):.4},{float(y):.4})",
                    (text_x_pos, text_y_pos),
                    cv2.FONT_HERSHEY_PLAIN, 1.5, text_color.value)

    @staticmethod
    def get_normalized_coordinate():
        if ROI_SELECTOR_PARAMS.cursor_position == None \
                or ROI_SELECTOR_PARAMS.cursor_position[0] == None \
                or ROI_SELECTOR_PARAMS.cursor_position[1] == None:
            return

        x = ROI_SELECTOR_PARAMS.cursor_position[0]
        y = ROI_SELECTOR_PARAMS.cursor_position[1]

        x_norm = x/ROI_SELECTOR_PARAMS.frame_width
        y_norm = y/ROI_SELECTOR_PARAMS.frame_height
        return (x_norm, y_norm)


def roi_selector(event, x, y, flags, params):
    x = util.minmax(0, params.frame_width-1, x)
    y = util.minmax(0, params.frame_height-1, y)
    ROI_SELECTOR_PARAMS.cursor_position = (x, y)

    if event == cv2.EVENT_LBUTTONDOWN:
        # reset certain parameters
        params._left_btn_up_clicked = True
        params._is_cursor_moving = False
        # params.box_end_position = None
        # set value
        params.box_start_position = (x, y)

    elif params._left_btn_up_clicked:
        if event == cv2.EVENT_MOUSEMOVE:
            params.box_end_position = (x, y)
            params._is_cursor_moving = True

        if event == cv2.EVENT_LBUTTONUP:
            params.box_end_position = (x, y)
            params.is_tracking = True
            params.is_update_required = True

            params._is_cursor_moving = False
            params._left_btn_up_clicked = False
