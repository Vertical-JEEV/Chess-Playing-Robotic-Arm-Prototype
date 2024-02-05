import pybullet
import pybullet_data

# Connect to the physics engine
client = pybullet.connect(pybullet.GUI)

# Now you can set the additional search path
pybullet.setAdditionalSearchPath(pybullet_data.getDataPath(), physicsClientId=client)

robot = pybullet.loadURDF(r"Hardware_module\braccio_description-master\urdf\braccio copy.urdf")

while True:
    pybullet.stepSimulation()