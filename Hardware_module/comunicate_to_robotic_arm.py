import serial
import serial.tools.list_ports
import pybullet
import pybullet_data
import math 
import time


physicsClient = pybullet.connect(pybullet.DIRECT)
pybullet.setAdditionalSearchPath(pybullet_data.getDataPath())

class ArduinoComunicator:
    BAUDRATE = 9600 # baudrate of the arduino


    def __init__(self):
        #self.COM_PORT = self.get_com_port()
        
        self.robotic_arm = pybullet.loadURDF(r"Hardware_module\braccio_description-master\urdf\braccio.urdf")
        self.end_effector_link_id = pybullet.getLinkState(self.robotic_arm, "gripper_movable")[10]
        self.target_orientation = pybullet.getQuaternionFromEuler([0, 0, 0])


        

    @staticmethod
    def get_com_port():
        TARGET_HARDWARE = "Arduino Uno"
        # we are looping through the com ports and checking if its an arduino uno
        for port in serial.tools.list_ports.comports():
            if TARGET_HARDWARE in port.description:
                return port.device
      

    def move_arm(self, target_position):
        joint_positions = pybullet.calculateInverseKinematics(self.robotic_arm, self.end_effector_link_id, target_position, self.target_orientation)

        # convert the angles to degrees, and convert them to string separated by a comma
        joint_positions = [str(math.degrees(angle)) for angle in joint_positions]
        joint_angle_string = ",".join(joint_positions)
        print(f"the angles are: {joint_angle_string}")

       
        arduino_connection = serial.Serial(self.COM_PORT, self.BAUDRATE)
        # need to add delay or else arduino or else arduino wont register it
        time.sleep(12)
        joint_angle_string = joint_angle_string.strip() # remove any whitespace
        joint_angle_string = joint_angle_string.encode() #  encode the string to bytes for arduino to understand
        arduino_connection.write(joint_angle_string)
        arduino_connection.close()


        


def testing():
    arduino = ArduinoComunicator()
    target_position = [10, 10, 10]
    arduino.move_arm(target_position)





testing()


        
    

