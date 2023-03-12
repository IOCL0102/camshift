import cv2
import numpy as np

from mouse_event.color_selector import color_selector
from mouse_event.color_selector import COLOR_SELECTOR_PARAMS
from mouse_event.roi_selector import roi_selector
from mouse_event.roi_selector import ROI_SELECTOR_PARAMS

from camshift_tracker import CamShiftTracker

from raspi_arduino_interface import CommandProcessor
from raspi_arduino_interface import RobotParamaters
from raspi_arduino_interface import Signal
from raspi_arduino_interface import ArduinoSerialSender
import util
from util import TERMINAL_TEXT_COLOR as ttc


def main():
    cap = cv2.VideoCapture(0)
    cap_width, cap_height = util.set_cap_width_height(cap, 640, 480)

    color_param = COLOR_SELECTOR_PARAMS()
    color_param.set_coordinate_normalization(True, 120)
    color_param.set_shift_left_param(True, 0.5, 0.5)

    roi_param = ROI_SELECTOR_PARAMS()

    cv2.namedWindow("main")
    cv2.setMouseCallback("main", color_selector, color_param)
    cv2.namedWindow("mask")
    cv2.setMouseCallback("mask", roi_selector, roi_param)

    mask = np.ones((cap_height, cap_width, 3), np.uint8)

    tracker = CamShiftTracker()
    tracker.set_color_mode(cv2.COLOR_BGR2HSV)

    keyboard_processor = CommandProcessor(
        ArduinoSerialSender(testing_phase=False))

    # I just simply name it
    virtual_robot_A = RobotParamaters()
    is_success_update = False

    while True:
        util.FPS.counter_on()
        is_read, frame = cap.read()
        # early return
        if not is_read:
            break

        # Updates the frames inside these params
        color_param.attach_frame(frame)
        roi_param.attach_frame(mask)

        #############################################################################
        # MAIN TRACKING OPERATION
        #############################################################################

        lower_bound = np.array(color_param.filter_lower_bound)
        upper_bound = np.array(color_param.filter_upper_bound)

        mask = cv2.inRange(frame, lower_bound, upper_bound)

        # is_updated_required : make sure it only updates value once
        # after LBUTTONUP is clicked
        if roi_param.is_update_required:
            is_success_update = tracker.update(frame, mask,
                                               roi_position=(
                                                   roi_param.box_start_position, roi_param.box_end_position))
            roi_param.is_update_required = False

        # is_tracking : make sure it runs after LBUTTONUP is clicked
        # is_success_update : make sure it runs after tracker.update function has successfully run
        if roi_param.is_tracking and is_success_update:
            track_box = tracker.track(frame, mask, is_draw=True, verbose=False)

            angle_x, angle_y = util.convert_to_angle(track_box,
                                                     convertion_func=color_param.coordinate_conversion)

            message = "MOVE," + str(angle_x) + "," + str(angle_y)
            ttc.info(message, highlight=True)
            # send message to arduino so that robot can know the coordinate of the target
            keyboard_processor.send_to_arduino(message)

        ####################################################################
        # KEY PRESSED HANDLING
        ####################################################################

        key_pressed = cv2.waitKey(1)
        if key_pressed != -1:
            signal = keyboard_processor.process(key_pressed, virtual_robot_A)

            if signal == Signal.TERMINATION_SIGNAL:
                break
            elif signal == Signal.NO_TRACKING_SIGNAL:
                roi_param.is_tracking = False

        ###########################################################
        # SET FRAME AND MASK ATTRIBUTES
        ###########################################################

        BGR_mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        roi_param.show_ROI_box(BGR_mask)
        roi_param.show_coordinate(BGR_mask)

        color_param.show_center_point()
        color_param.show_coordinate()

        util.FPS.show_FPS(frame)
        util.insert_info_to_frame(frame, virtual_robot_A)

        cv2.imshow("main", frame)
        cv2.imshow("mask", BGR_mask)

    # Release the video capture object and close all windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
