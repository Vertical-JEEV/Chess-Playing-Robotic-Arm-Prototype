import serial
import serial.tools.list_ports
import time
import pybullet as p
import math


class ArduinoComunicator:
    BAUDRATE = 9600 # baudrate of the arduino


    def __init__(self):
        #self.COM_PORT = self.get_com_port()
        p.connect(p.DIRECT)
        p.setAdditionalSearchPath(r"Hardware_module\braccio_description")
        self.braccio_arm = p.loadURDF(r"Hardware_module\braccio_description\urdf\braccio.urdf")
        self.end_effector_id = next(i for i in range(p.getNumJoints(self.braccio_arm)) if p.getJointInfo(self.braccio_arm, i)[1].decode() == "gripper_movable")

        
       
        

    @staticmethod
    def get_com_port():
        TARGET_HARDWARE = "Arduino Uno"
        # we are looping through the com ports and checking if its an arduino uno
        for port in serial.tools.list_ports.comports():
            if TARGET_HARDWARE in port.description:
                return port.device
      

    def move_arm(self, target_position):
        joint_positions = p.calculateInverseKinematics(self.braccio_arm, self.end_effector_id, target_position)
        # convert the joint_positions to degrees using math and then round the joint positions to 2 decimal places and convert them to string separated by a comma
        joint_positions = [round(math.degrees(joint_position), 2) for joint_position in joint_positions]
        joint_angle_string = ",".join(map(str, joint_positions))
        print(f"\nThe angles to move the robot are: {joint_angle_string}")
        
      

        

       
        # arduino_connection = serial.Serial(self.COM_PORT, self.BAUDRATE)
        # # need to add delay or else arduino or else arduino wont register it
        # time.sleep(12)
        # joint_angle_string = joint_angle_string.strip() # remove any whitespace
        # joint_angle_string = joint_angle_string.encode() #  encode the string to bytes for arduino to understand
        # arduino_connection.write(joint_angle_string)
        # arduino_connection.close()


        


def testing():
    arduino = ArduinoComunicator()
    target_position = [0.,0.5,0.5]
    arduino.move_arm(target_position)





testing()


        
    

