import numpy as np
from enum import Enum
import cv2
import time


class COLOR(Enum):
    WHITE_BGR = (255, 255, 255)
    BLACK_BGR = (0, 0, 0)
    RED_BGR = (0, 0, 255)
    ORANGE_BGR = (0, 162, 255)
    YELLOW_BGR = (0, 255, 255)
    GREEN_BGR = (0, 255, 0)
    BLUE_BGR = (255, 0, 0)
    MAGENTA_BGR = (255, 0, 255)
    PURPLE_BGR = (128, 0, 128)


def minmax(lower_limit, upper_limit, target):
    """
        This function makes sure the target falls between lower_limit and upper_limit
    """
    target = np.asarray(target)
    return np.maximum(lower_limit, np.minimum(upper_limit, target))


def normalize(target, min, max):
    return (target-min)/(max-min)


def insert_info_to_frame(frame, robot_param, text_color=COLOR.RED_BGR):
    cv2.putText(frame, "Mode: " + robot_param.mode, (20, 40),
                cv2.FONT_HERSHEY_PLAIN, 1.2, text_color.value)
    cv2.putText(frame, "PWM: " + str(round(robot_param.rotating_disc_PWM)),
                (20, 60), cv2.FONT_HERSHEY_PLAIN, 1.2, text_color.value)
    # cv2.putText(frame, "FPS: " + str(round(FPS)), (20, 35),
    #            cv2.FONT_HERSHEY_PLAIN, 1.2, text_color.value)


def set_cap_width_height(cap, width, height):
    """
        ### Returns:
            tuple: (width, height)
    """
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))


def check_available_size(cap: cv2.VideoCapture = cv2.VideoCapture(0)):
    max_width = 2000
    max_height = 2000
    step_size = 200
    available_size = set()
    for w in range(0, max_width+step_size, step_size):
        for h in range(0, max_height+step_size, step_size):
            print(f"testing with width:{w} height:{h}")
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            available_size.add((width, height))

    print(available_size)
    return available_size


class FPS:
    start_time = 0
    FPS = 0
    num_frame = 0
    total_seconds = 0

    def counter_on():
        FPS.start_time = time.time()

    def show_FPS(frame, coordinate=(20, 20), text_color=COLOR.RED_BGR):
        # Calculate FPS
        FPS.total_seconds += time.time() - FPS.start_time
        FPS.num_frame += 1
        if(FPS.total_seconds > 0.99):
            FPS.FPS = FPS.num_frame / FPS.total_seconds
            FPS.total_seconds = 0
            FPS.num_frame = 0

        cv2.putText(frame, "FPS: " + str(round(FPS.FPS)), coordinate,
                    cv2.FONT_HERSHEY_PLAIN, 1.2, text_color.value)


class TERMINAL_TEXT_COLOR:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    UNDERLINE = '\033[4m'
    RED_HIGHLIGHT = '\x1b[6;30;41m'
    GREEN_HIGHLIGHT = '\x1b[6;30;42m'
    YELLOW_HIGHLIGHT = '\x1b[6;30;43m'

    RESET = '\033[0m'

    error_printable = True
    info_printable = True
    warning_printable = True

    def set_printable(is_show_error, is_show_info, is_show_warning):
        TERMINAL_TEXT_COLOR.error_printable = is_show_error
        TERMINAL_TEXT_COLOR.info_printable = is_show_info
        TERMINAL_TEXT_COLOR.warning_printable = is_show_warning

    @staticmethod
    def error(text, highlight=False):
        if TERMINAL_TEXT_COLOR.error_printable:
            prefix = TERMINAL_TEXT_COLOR.RED_HIGHLIGHT if highlight else TERMINAL_TEXT_COLOR.RED
            print(prefix + "ERROR::" + str(text) + TERMINAL_TEXT_COLOR.RESET)

    @staticmethod
    def info(text, highlight=False):
        if TERMINAL_TEXT_COLOR.info_printable:
            prefix = TERMINAL_TEXT_COLOR.GREEN_HIGHLIGHT if highlight else TERMINAL_TEXT_COLOR.GREEN
            print(prefix + "INFO::" + str(text) + TERMINAL_TEXT_COLOR.RESET)

    @staticmethod
    def warning(text, highlight=False):
        if TERMINAL_TEXT_COLOR.warning_printable:
            prefix = TERMINAL_TEXT_COLOR.YELLOW_HIGHLIGHT if highlight else TERMINAL_TEXT_COLOR.YELLOW
            print(prefix + "WARNING::" + str(text) + TERMINAL_TEXT_COLOR.RESET)
