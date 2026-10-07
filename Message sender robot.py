import sim
import time

# Connect to CoppeliaSim for Robot A
sim.simxFinish(-1)  # Close all opened connections
clientID_A = sim.simxStart('127.0.0.1', 28000, True, True, 5000, 5)  # Connect to CoppeliaSim

if clientID_A != -1:
    print('Robot A connected to CoppeliaSim')

    while True:
        # Send a message to Robot B
        message = "Joy ram"
        sim.simxSetStringSignal(clientID_A, 'RobotA_to_RobotB', message, sim.simx_opmode_oneshot)
        print('sending')
        # Wait for a short period before sending the next message
        time.sleep(1)

    # Close the connection when done
    sim.simxFinish(clientID_A)
else:
    print('Failed to connect to CoppeliaSim for Robot A')
