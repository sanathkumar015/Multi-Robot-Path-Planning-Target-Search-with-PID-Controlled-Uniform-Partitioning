import sim
import time

# Connect to CoppeliaSim for Robot B
sim.simxFinish(-1)  # Close all opened connections
clientID_B = sim.simxStart('127.0.0.1', 19997, True, True, 5000, 5)  # Connect to CoppeliaSim

if clientID_B != -1:
    print('Robot B connected to CoppeliaSim')

    # Initialize the signal reception (required to set up the signal in a streaming mode)
    sim.simxGetStringSignal(clientID_B, 'RobotA_to_RobotB', sim.simx_opmode_streaming)

    while True:
        # Continuously check for a message from Robot A
        returnCode, signalValue = sim.simxGetStringSignal(clientID_B, 'RobotA_to_RobotB', sim.simx_opmode_buffer)
        if returnCode == sim.simx_return_ok and signalValue:
            print("Robot B received:", signalValue)
        else:
            print("Waiting for message from Robot A...")

        time.sleep(1)

    # Close the connection when done
    sim.simxFinish(clientID_B)
else:
    print('Failed to connect to CoppeliaSim for Robot B')
