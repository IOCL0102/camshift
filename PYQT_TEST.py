import sys
import cv2
from PyQt5.QtCore import QTimer, QPoint, QRect, Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QWidget

from mouse_event.color_selector import COLOR_SELECTOR_PARAMS
from mouse_event.color_selector import color_selector
import util
import numpy as np


class VideoLabel(QLabel):
    def __init__(self, selector_param=COLOR_SELECTOR_PARAMS):
        super().__init__()  # Call parent class' __init__() method
        self.selector_param = COLOR_SELECTOR_PARAMS
        self.pixmap = None

    def mousePressEvent(self, event):
        c1_range = self.selector_param.filter_color_range[0]
        c2_range = self.selector_param.filter_color_range[1]
        c3_range = self.selector_param.filter_color_range[2]

        c1 = self.selector_param.cursor_color[0]
        c2 = self.selector_param.cursor_color[1]
        c3 = self.selector_param.cursor_color[2]

        self.selector_param.filter_lower_bound = np.array(
            (c1 - c1_range, c2 - c2_range, c3 - c3_range))
        self.selector_param.filter_upper_bound = np.array(
            (c1 + c1_range, c2 + c2_range, c3 + c3_range))

        # make sure the boundary fall from 0 to 255
        channel_max_value = COLOR_SELECTOR_PARAMS.channel_max_value
        self.selector_param.filter_lower_bound = util.minmax(
            0, channel_max_value, self.selector_param.filter_lower_bound)
        self.selector_param.filter_upper_bound = util.minmax(
            0, channel_max_value, self.selector_param.filter_upper_bound)

    def mouseMoveEvent(self, event):
        self.selector_param.cursor_position = (x, y)

        y = util.minmax(0, self.selector_param.frame.shape[0]-1, [y])[0]
        x = util.minmax(0, self.selector_param.frame.shape[1]-1, [x])[0]

        # channel is a more general name to describe RGB, HSV, ...
        c1 = self.selector_param.frame[y, x, 0]
        c2 = self.selector_param.frame[y, x, 1]
        c3 = self.selector_param.frame[y, x, 2]
        self.selector_param.cursor_color = (c1, c2, c3)


class VideoCapture(QDialog):
    def __init__(self):
        super().__init__()

        # Set up the video capture object
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Set up the GUI
        self.label = VideoLabel()
        self.label.resize(640, 480)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.display_frame)
        self.timer.start(1)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

    def display_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Convert the frame to RGB format
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert the frame to QImage
            img = QImage(frame, frame.shape[1],
                         frame.shape[0], QImage.Format_RGB888)

            # Display the image on the label widget
            self.label.pixmap = QPixmap.fromImage(img)
            self.label.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    video_capture = VideoCapture()
    video_capture.show()

    sys.exit(app.exec_())
