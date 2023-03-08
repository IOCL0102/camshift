import cv2
import numpy as np
import util
from util import COLOR
from util import TERMINAL_TEXT_COLOR as ttc


class COLOR_SELECTOR_PARAMS:
    """
        This class act as an parameters to be passed into the color selector mouse event
    """
    frame: list = None
    cursor_position: tuple = None
    cursor_color: tuple = None

    is_shift_left: bool = False
    shift_left_ratio_x: float = 0.5
    shift_left_ratio_y: float = 0.5

    is_normalize: bool = False
    normalized_max: int = None

    filter_color_range = [20, 20, 20]
    # boundary values will be changed(update) frequently, these are just initial value
    filter_lower_bound = [0, 0, 0]
    filter_upper_bound = [255, 255, 255]

    channel_max_value = 255

    unwantedColor = []

    @staticmethod
    def set_channel_max_value(max_value):
        COLOR_SELECTOR_PARAMS.channel_max_value = max_value

    @staticmethod
    def set_shift_left_param(is_shift_left: bool, ratio_x: float = 0.5, ratio_y: float = 0.5):
        COLOR_SELECTOR_PARAMS.is_shift_left = is_shift_left
        COLOR_SELECTOR_PARAMS.shift_left_ratio_x = ratio_x
        COLOR_SELECTOR_PARAMS.shift_left_ratio_y = ratio_y

    @staticmethod
    def set_coordinate_normalization(is_normalize, normalized_max=100):
        COLOR_SELECTOR_PARAMS.is_normalize = is_normalize
        COLOR_SELECTOR_PARAMS.normalized_max = normalized_max

    @staticmethod
    def attach_frame(frame):
        COLOR_SELECTOR_PARAMS.frame = frame

    @staticmethod
    def set_filter_range(channel_1, channel_2, channel_3):
        # channel is a more general name to describe RGB, HSV, ...
        channel_max_value = COLOR_SELECTOR_PARAMS.channel_max_value
        c1 = util.minmax(0, channel_max_value, channel_1)
        c2 = util.minmax(0, channel_max_value, channel_2)
        c3 = util.minmax(0, channel_max_value, channel_3)
        COLOR_SELECTOR_PARAMS.filter_color_range = (c1, c2, c3)

    @staticmethod
    def show_center_point(frame=None):
        frame = COLOR_SELECTOR_PARAMS.frame if frame is None else frame
        frame_width = np.asarray(COLOR_SELECTOR_PARAMS.frame).shape[1]
        frame_height = np.asarray(COLOR_SELECTOR_PARAMS.frame).shape[0]
        mid_point = [int(round(frame_width * COLOR_SELECTOR_PARAMS.shift_left_ratio_x)),
                     int(round(frame_height * COLOR_SELECTOR_PARAMS.shift_left_ratio_y))]

        cv2.circle(frame, mid_point, 2, COLOR.ORANGE_BGR.value, -1)
        cv2.circle(frame, mid_point, 50, COLOR.ORANGE_BGR.value, 2)

    @staticmethod
    def show_coordinate(frame=None, text_color=COLOR.RED_BGR):
        if not isinstance(text_color, COLOR):
            ttc.warning("text_color is not instance of COLOR Enum class")
            return

        if COLOR_SELECTOR_PARAMS.cursor_position == None \
                or COLOR_SELECTOR_PARAMS.cursor_position[0] == None \
                or COLOR_SELECTOR_PARAMS.cursor_position[1] == None:
            return

        frame = COLOR_SELECTOR_PARAMS.frame if frame is None else frame
        x = y = text_x_pos = text_y_pos = 0.0

        if COLOR_SELECTOR_PARAMS.is_normalize is True:
            coordinate = COLOR_SELECTOR_PARAMS.get_normalized_coordinate()
            x = coordinate[0] * COLOR_SELECTOR_PARAMS.normalized_max
            y = coordinate[1] * COLOR_SELECTOR_PARAMS.normalized_max
        else:
            x = COLOR_SELECTOR_PARAMS.cursor_position[0]
            y = COLOR_SELECTOR_PARAMS.cursor_position[1]

        text_x_pos, text_y_pos, frame_width, frame_height = COLOR_SELECTOR_PARAMS._get_text_pos()

        if COLOR_SELECTOR_PARAMS.is_shift_left and COLOR_SELECTOR_PARAMS.is_normalize:
            x -= COLOR_SELECTOR_PARAMS.normalized_max * \
                COLOR_SELECTOR_PARAMS.shift_left_ratio_x
            y -= COLOR_SELECTOR_PARAMS.normalized_max * \
                COLOR_SELECTOR_PARAMS.shift_left_ratio_y
            y = y*-1
        elif COLOR_SELECTOR_PARAMS.is_shift_left and not COLOR_SELECTOR_PARAMS.is_normalize:
            x -= frame_width*COLOR_SELECTOR_PARAMS.shift_left_ratio_x
            y -= frame_height*COLOR_SELECTOR_PARAMS.shift_left_ratio_y
            y = y*-1

        cv2.putText(frame, f"({float(x):.4},{float(y):.4})",
                    (text_x_pos, text_y_pos),
                    cv2.FONT_HERSHEY_PLAIN, 1.5, text_color.value)

    @staticmethod
    def _get_text_pos():
        # Make sure the coordinate text display always visible to the screen
        frame_width = np.asarray(COLOR_SELECTOR_PARAMS.frame).shape[1]
        frame_height = np.asarray(COLOR_SELECTOR_PARAMS.frame).shape[0]
        boundary_x = frame_width/5
        boundary_y = frame_height/5

        if COLOR_SELECTOR_PARAMS.cursor_position[0] < frame_width-boundary_x:
            text_x_pos = int(COLOR_SELECTOR_PARAMS.cursor_position[0]+10)
        else:
            text_x_pos = int(
                COLOR_SELECTOR_PARAMS.cursor_position[0]-boundary_x*1.5)

        if COLOR_SELECTOR_PARAMS.cursor_position[1] > boundary_y:
            text_y_pos = int(COLOR_SELECTOR_PARAMS.cursor_position[1]-10)
        else:
            text_y_pos = int(
                COLOR_SELECTOR_PARAMS.cursor_position[1]+boundary_y*0.2)

        return (text_x_pos, text_y_pos, frame_width, frame_height)

    @staticmethod
    def get_normalized_coordinate(is_shift_left=False):
        if COLOR_SELECTOR_PARAMS.cursor_position == None \
                or COLOR_SELECTOR_PARAMS.cursor_position[0] == None \
                or COLOR_SELECTOR_PARAMS.cursor_position[1] == None:
            return

        x = COLOR_SELECTOR_PARAMS.cursor_position[0]
        y = COLOR_SELECTOR_PARAMS.cursor_position[1]
        frame_width = np.asarray(COLOR_SELECTOR_PARAMS.frame).shape[1]
        frame_height = np.asarray(COLOR_SELECTOR_PARAMS.frame).shape[0]

        x_norm = util.normalize(x, 0, frame_width)
        y_norm = util.normalize(y, 0, frame_height)

        if is_shift_left:
            x_norm -= x_norm*COLOR_SELECTOR_PARAMS.shift_left_ratio
            y_norm -= y_norm*COLOR_SELECTOR_PARAMS.shift_left_ratio

        return (x_norm, y_norm)

    @staticmethod
    def coordinate_conversion(point):
        frame_width = np.asarray(COLOR_SELECTOR_PARAMS.frame).shape[1]
        frame_height = np.asarray(COLOR_SELECTOR_PARAMS.frame).shape[0]

        x = point[0]
        y = point[1]

        if COLOR_SELECTOR_PARAMS.is_normalize:
            x_norm = util.normalize(point[0], 0, frame_width)
            y_norm = util.normalize(point[1], 0, frame_height)
            x = x_norm * COLOR_SELECTOR_PARAMS.normalized_max
            y = y_norm * COLOR_SELECTOR_PARAMS.normalized_max

        if COLOR_SELECTOR_PARAMS.is_shift_left and COLOR_SELECTOR_PARAMS.is_normalize:
            x -= COLOR_SELECTOR_PARAMS.normalized_max * \
                COLOR_SELECTOR_PARAMS.shift_left_ratio_x
            y -= COLOR_SELECTOR_PARAMS.normalized_max * \
                COLOR_SELECTOR_PARAMS.shift_left_ratio_y
        elif COLOR_SELECTOR_PARAMS.is_shift_left and COLOR_SELECTOR_PARAMS.is_normalize is False:
            x -= frame_width*COLOR_SELECTOR_PARAMS.shift_left_ratio_x
            y -= frame_height*COLOR_SELECTOR_PARAMS.shift_left_ratio_y

        y = y*-1
        return(x, y)


def color_selector(event, x, y, flag, params):
    params.cursor_position = (x, y)

    y = util.minmax(0, params.frame.shape[0]-1, [y])[0]
    x = util.minmax(0, params.frame.shape[1]-1, [x])[0]

    # channel is a more general name to describe RGB, HSV, ...
    c1 = params.frame[y, x, 0]
    c2 = params.frame[y, x, 1]
    c3 = params.frame[y, x, 2]
    params.cursor_color = (c1, c2, c3)

    if(event == cv2.EVENT_LBUTTONDOWN):
        c1_range = params.filter_color_range[0]
        c2_range = params.filter_color_range[1]
        c3_range = params.filter_color_range[2]

        params.cursor_color = (c1, c2, c3)
        params.filter_lower_bound = np.array(
            (c1 - c1_range, c2 - c2_range, c3 - c3_range))
        params.filter_upper_bound = np.array(
            (c1 + c1_range, c2 + c2_range, c3 + c3_range))

        # make sure the boundary fall from 0 to 255
        channel_max_value = COLOR_SELECTOR_PARAMS.channel_max_value
        params.filter_lower_bound = util.minmax(
            0, channel_max_value, params.filter_lower_bound)
        params.filter_upper_bound = util.minmax(
            0, channel_max_value, params.filter_upper_bound)

    if(event == cv2.EVENT_RBUTTONDOWN):
        params.unwantedColor.append(np.array([c1, c2, c3]))
        ttc.info("added color: ", np.array([c1, c2, c3]))
