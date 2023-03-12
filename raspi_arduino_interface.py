import serial
import time
from util import TERMINAL_TEXT_COLOR as ttc
from dataclasses import dataclass


@dataclass
class RobotParamaters:
    """
    Struct-like dataclass that stores various parameters that manipulate the behavior of the robot
    """
    mode: str = ""
    is_disc_moving: bool = False
    rotating_disc_PWM: int = 60
    min_PWM: int = 0
    max_PWM: int = 255


class Signal:
    """
    Class that defines signals, which provides meaning to integer value for further processing
    """
    NO_TRACKING_SIGNAL = 1
    TERMINATION_SIGNAL = 5


class ArduinoSerialSender:
    """
    Class that sends message to arduino through serial communication

    ### Attributes:
        is_testing_phase (bool): When it is true, it does not establish connection to dev/ttyACMx and thus does not send message to arduino.      

    ==================================================
    ### Overall sending procedure:
    ==================================================
    #### Rasberrypi side:
    ArduinoSerialSender    
    ---establish connection---> rasberrypi serial port
    ---connection established---> call send_to_arduino() method

    #### Arduino side
    ---message sent---> arduino receive the encoded message
    ---message decode---> receive the exact message
    """

    def __init__(self, testing_phase=False):
        """
        Init function which it tries to establish connection with the serial port of rasberrypi
        """
        self.is_testing_phase = testing_phase

        if not self.is_testing_phase:
            try:
                try:
                    ttc.info("Connecting /dev/ttyACM0 ...")
                    self.ser = serial.Serial(
                        '/dev/ttyACM0', 115200, timeout=1.0)
                except:
                    ttc.warning("Failure to connect /dev/ttyACM0")
                    ttc.info("Connecting /dev/ttyACM1 ...")
                    self.ser = serial.Serial(
                        '/dev/ttyACM1', 115200, timeout=1.0)
            except:
                ttc.error("Connection Failed", highlight=True)
                self.is_testing_phase = True
            else:
                ttc.info("Succesfully connected")
                time.sleep(3)
                self.ser.reset_input_buffer()

    def send_to_arduino(self, message):
        """
        This method send the message to arduino through serial communication

        ### Args:
            message (str): The message that sends to arduino
        """
        message += "\n"
        self.ser.write(message.encode('utf-8')
                       ) if not self.is_testing_phase else None


class CommandProcessor:
    """
    A class that process pressed key from rasberry pi and send to arduino

    ### Attributes:
        sender (ArduinoSerialSender): Used to send message to arduino throgh serial communication
        key_action_table (dictionary): Used to store pressed key and the function operation pair. When a key is pressed, the respective function will be called.


    ### Important notes:
        The functions stored in key_action_table should only receive one parameters, which is object of RobotParamaters

    """

    def __init__(self, sender):
        """
        Initialize a new instance for the Command Processor class
        """

        self.sender = sender
        self.key_action_table = {}

        NUMPAD_1 = 49
        NUMPAD_2 = 50
        NUMPAD_3 = 51
        NUMPAD_5 = 53
        ESC_KEY = 27

        # Termination
        self.key_action_table[ESC_KEY] = lambda robot_param: Signal.TERMINATION_SIGNAL

        # Up and down
        self.key_action_table[ord('w')] = lambda robot_param: self.simple_send(
            robot_param, "up", "W")
        self.key_action_table[ord('s')] = lambda robot_param: self.simple_send(
            robot_param, "down", "S")

        # Rotation move
        self.key_action_table[ord('a')] = lambda robot_param: self.simple_send(
            robot_param, "left", "A")
        self.key_action_table[ord('d')] = lambda robot_param: self.simple_send(
            robot_param, "right", "D")

       # Translation move
        self.key_action_table[NUMPAD_1] = lambda robot_param: self.simple_send(
            robot_param, "move left", "MOVE_LEFT")
        self.key_action_table[NUMPAD_2] = lambda robot_param: self.simple_send(
            robot_param, "move down", "MOVE_BACK")
        self.key_action_table[NUMPAD_3] = lambda robot_param: self.simple_send(
            robot_param, "move right", "MOVE_RIGHT")
        self.key_action_table[NUMPAD_5] = lambda robot_param: self.simple_send(
            robot_param, "move front", "MOVE_FRONT")

        # Reload and Shoot
        self.key_action_table[ord('r')] = lambda robot_param: self.simple_send(
            robot_param, "reload", "RELOAD")
        self.key_action_table[ord('c')] = lambda robot_param: self.simple_send(
            robot_param, "shoot", "SHOOT")

        # Reload and Shoot
        self.key_action_table[ord('i')] = self.__add_rotating_disc_PWM_send
        self.key_action_table[ord('k')] = self.__minus_rotating_disc_PWM_send

        # Activate and Deactivate disc
        self.key_action_table[ord('z')] = self.__activate_disc_send
        self.key_action_table[ord('x')] = self.__deactivate_disc_send

        # Stop tracking
        self.key_action_table[ord('q')] = self.__stop_tracking

    def process(self, pressed_key, robot_param):
        """
        This method process the pressed_key and perform the action based on pressed_key

        For specific function please refers to key_action_table

        ### Args:
            pressed_key     (int): The input from rasberrypi ( commonly by keyboard )
            robot_param     (string) : The robot which this parameters will be passed in to the argument of the respective action function

        ### Returns: 
            None
        """
        # if pressed_key not found, return False
        if self.key_action_table.get(pressed_key, False):
            return self.key_action_table[pressed_key](robot_param)

        else:
            ttc.warning(
                "Key not defined in key action table, thus no operation performed")
        return None

    def send_to_arduino(self, message):
        self.sender.send_to_arduino(message)

    def simple_send(self, robot_param, mode=None, message=""):
        """
        This method only perform changing the mode of the robot parameters, and send message to arduino only

        ### Args:
            robot_param (RobotParamaters): Used to change the mode
            mode                (string) : It is used to assign to the robot_param.mode value
            message             (string) : This exact message will be sent to arduino using serial communication

        ### Returns:
            None
        """
        robot_param.mode = mode
        self.sender.send_to_arduino(message)

    def __add_rotating_disc_PWM_send(self, robot_param):
        """
        This method add the value of the rotating disc PWM of the robot, and send the message to arduino

        ### Args:
            robot_param (RobotParamaters): Used to modify the PWM value and mode

        ### Returns: 
            None
        """
        if not robot_param.rotating_disc_PWM + 5 > robot_param.max_PWM:
            robot_param.rotating_disc_PWM += 5
        else:
            ttc.warning("PWM value has reached its maximum value")

        robot_param.mode = "add Disc PWM"
        if(robot_param.is_disc_moving == True):
            message = "START_DISC," + str(robot_param.rotating_disc_PWM)
            self.sender.send_to_arduino(message)

    def __minus_rotating_disc_PWM_send(self, robot_param):
        """
        This method minus the value of the rotating disc PWM of the robot, and send the message to arduino

        ### Args:
            robot_param (RobotParamaters): Used to modify the PWM value and mode

        ### Returns: 
            None
        """
        if not robot_param.rotating_disc_PWM - 5 < robot_param.min_PWM:
            robot_param.rotating_disc_PWM -= 5
        else:
            ttc.warning("PWM value has reached its minimum value")

        robot_param.mode = "minus Disc PWM"
        if(robot_param.is_disc_moving == True):
            message = "START_DISC," + str(robot_param.rotating_disc_PWM)
            self.sender.send_to_arduino(message)

    def __activate_disc_send(self, robot_param):
        """
        This method set the mode to activate (making the disc runs), and send the message to arduino

        ### Args:
            robot_param (RobotParamaters): Used to modify the is_disc_moving parameter value and mode

        ### Returns: 
            None
        """
        robot_param.mode = "Activate Disc"
        robot_param.is_disc_moving = True
        message = "START_DISC," + str(robot_param.rotating_disc_PWM)
        self.sender.send_to_arduino(message)

    def __deactivate_disc_send(self, robot_param):
        """
        This method set the mode to deactivate (making the disc stops), and send the message to arduino

        ### Args:
            robot_param (RobotParamaters): Used to modify the is_disc_moving parameter value and mode

        ### Returns: 
            None
        """
        robot_param.mode = "Deactivate Disc"
        robot_param.is_disc_moving = False
        message = "STOP_DISC"
        self.sender.send_to_arduino(message)

    def __stop_tracking(self, robot_param):
        """
        This method set the mode to stop tracking, and send the message to arduino to let the robot stop moving

        ### Args:
            robot_param (RobotParamaters): Used to modify the is_disc_moving parameter value and mode

        ### Returns: 
            Signal.NO_TRACKING_SIGNAL ( equivalent to integer 1 )
        """
        robot_param.mode = "stop tracking"
        message = "STOP"
        self.sender.send_to_arduino(message)
        return Signal.NO_TRACKING_SIGNAL
