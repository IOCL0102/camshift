import cv2
import numpy as np


class CamShiftTracker:
    """
    A class that used to perform camshift tracking algorithm

    ### Attributes:
        bbox   (tuple): Bounding box,  which is the target that the camshift tracker tracks. Format as following, (x0, y0, box_width, box_height)

        roi_hist      : Calculation result by the cv2.calcHist() function

        term_crit     : A parameters that used for cv2.calcHist()

        color_mode    : Color convertion index based on cv2, example -> cv2.BGR2HSV , cv2.BGR2RGBV, etc.

        bin_size  (int): size of the intensity level for histogram calculation. Higher bin_size, more pay attention to detail of the image    

    """

    def __init__(self, bin_size=16):
        """
        Init function of the CamShiftTracker class
        """
        self.bbox = None
        self.roi_hist = None
        self.term_crit = (cv2.TERM_CRITERIA_EPS |
                          cv2.TERM_CRITERIA_COUNT, 10, 1)
        self.color_mode = None
        self.bin_size = bin_size

    def set_color_mode(self, color_mode):
        """
        This method sets the color_mode

        ### Args:
            color_mode : Example-> cv2.BGR2HSV , cv2.BGR2RGBV, etc.

        ### Returns:
            None
        """
        self.color_mode = color_mode

    def update(self, frame, mask, roi_position):
        """
        This methods updates the parameters that will be used for tracking in the track method

        ### Args:
            frame                 (array): Frame that captures by the video stream
            mask                  (array): Mask that filtered by cv2.inRange() function
            roi_position (tuple in tuple): Consist of the starting and ending position of the bounding box ( region of interest ), format as following 
            ((x1,y1), (x2,y2))

        ### Returns:
            bool: Returns true if sucessfully updated the parameters else return false

        ### Notes:
            Note that the first index of opencv frame array is y not x
            format please refers as following as example

            frame[y,x,channel]
            channel   0,1,2   B,G,R CHANNEL

        """

        # Input validation
        if roi_position[1] == None or roi_position[0] == None \
                or roi_position[0][0] - roi_position[1][0] == 0 \
                or roi_position[0][1] - roi_position[1][1] == 0:
            return False

        # Find box width and box height
        box_width = abs(roi_position[0][0] - roi_position[1][0])
        box_height = abs(roi_position[0][1] - roi_position[1][1])

        # Set the smallest x-axis value as starting point
        x0 = min(roi_position[0][0], roi_position[1][0])
        y0 = min(roi_position[0][1], roi_position[1][1])

        # Define bounding box
        self.bbox = (x0, y0, box_width, box_height)

        # Set Region of Interest
        frame_roi = np.array(frame[y0: y0 + box_height, x0: x0 + box_width])
        if self.color_mode is not None:
            frame_roi = cv2.cvtColor(frame_roi, self.color_mode)

        mask_roi = np.array(mask[y0: y0 + box_height, x0: x0 + box_width])

        # Calculate historgram
        self.roi_hist = cv2.calcHist([frame_roi], [0], mask_roi, [
                                     self.bin_size], [0, 180])

        # Normalize y-axis (number of pixel)
        # -> different picture might have different size (pixels)
        cv2.normalize(self.roi_hist, self.roi_hist, 0, 255, cv2.NORM_MINMAX)

        # Flatten to a 1d-numpy array
        self.roi_hist = self.roi_hist.reshape(-1)

        return True

    def track(self, frame, mask, is_draw=True, verbose=False):
        """
        This method use the arguments that calculated by the update method and perform the camshift tracking algorithm

        ### Args:
            frame   (array): Frame that captures by the video stream

            mask    (array): Current mask that filtered by cv2.inRange() for current frame

            is_draw  (bool): When set to true, it draws the bounding box to the frame

            verbose  (bool): When set to true, it prints the center point of the tracking object (output of the camshift algorithm)

        ### Returns:
            track_box: (center_x, center_y), (width, height), angle

        ### Notes:
            bbox format
            (center_x, center_y, width, height)

            track_box format
            (center_x, center_y), (width, height), angle

            (center_x, center_y): The (x, y) coordinates of the center of the rectangle.
            (width, height): The width and height of the rectangle.
            angle: The angle of rotation of the minimum area rectangle in degrees.
        """
        # Apply meanshift algorithm to track the object

        ref = cv2.cvtColor(
            frame, self.color_mode) if self.color_mode is not None else frame

        # return a gray scale image where each pixel represent the likelyhood probability comparing the roi_hist
        prob = cv2.calcBackProject([ref], [0], self.roi_hist, [0, 180], 1)

        # it is used to ignore the rest pixel value except the mask roi
        prob &= mask

        track_box, self.bbox = cv2.CamShift(prob, self.bbox, self.term_crit)

        target_mid_point = (round(track_box[0][0]), round(track_box[0][1]))

        if is_draw:
            cv2.circle(frame, target_mid_point, 5, (0, 0, 255), -1)
            cv2.ellipse(frame, track_box, (0, 255, 0), 2)

        if verbose:
            print(target_mid_point)

        return track_box
