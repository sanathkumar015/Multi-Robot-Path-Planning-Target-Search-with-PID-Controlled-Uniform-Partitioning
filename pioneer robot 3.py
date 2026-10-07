import math
import time
import copy
from robot_motion_communication_utils import *
import socket
import threading
from central_dictionary_handling_utils_sept24 import*

running = True

robot_name = 'robot3'
RFID_range = 2
#copy the grid point from the result of Multi Robot Area Allocation & TSP opt- Main file - Sept 24 file
#sequence = [(-25, 0), (-25.0, -1.0), (-25.0, -2.0), (-25.0, -3.0), (-25.0, -4.0), (-25.0, -5.0), (-24.0, -5.0), (-24.0, -4.0), (-24.0, -3.0), (-24.0, -2.0), (-24.0, -1.0), (-24.0, 0.0), (-24.0, 1.0), (-25.0, 1.0), (-25.0, 2.0), (-25.0, 3.0), (-25.0, 4.0), (-24.0, 4.0), (-24.0, 3.0), (-24.0, 2.0), (-23.0, 2.0), (-23.0, 1.0), (-23.0, 0.0), (-23.0, -1.0), (-23.0, -2.0), (-23.0, -3.0), (-23.0, -4.0), (-23.0, -5.0), (-22.0, -5.0), (-22.0, -4.0), (-22.0, -3.0), (-22.0, -2.0), (-22.0, -1.0), (-22.0, 0.0), (-22.0, 1.0), (-22.0, 2.0), (-22.0, 3.0), (-23.0, 3.0), (-23.0, 4.0), (-22.0, 4.0), (-21.0, 4.0), (-21.0, 3.0), (-21.0, 2.0), (-21.0, 1.0), (-21.0, 0.0), (-21.0, -1.0), (-21.0, -2.0), (-21.0, -3.0), (-21.0, -4.0), (-21.0, -5.0), (-20.0, -5.0), (-20.0, -4.0), (-20.0, -3.0), (-20.0, -2.0), (-20.0, -1.0), (-20.0, 0.0), (-20.0, 1.0), (-20.0, 2.0), (-20.0, 3.0), (-20.0, 4.0), (-19.0, 4.0), (-19.0, 3.0), (-19.0, 2.0), (-19.0, 1.0), (-19.0, 0.0), (-19.0, -1.0), (-19.0, -2.0), (-19.0, -3.0), (-19.0, -4.0), (-19.0, -5.0), (-18.0, -5.0), (-18.0, -4.0), (-18.0, -3.0), (-18.0, -2.0), (-18.0, -1.0), (-18.0, 0.0), (-18.0, 1.0), (-18.0, 2.0), (-18.0, 3.0), (-18.0, 4.0), (-17.0, 4.0), (-17.0, 3.0), (-17.0, 2.0), (-17.0, 1.0), (-17.0, 0.0), (-17.0, -1.0), (-17.0, -2.0), (-17.0, -3.0), (-17.0, -4.0), (-17.0, -5.0), (-16.0, -5.0), (-16.0, -4.0), (-16.0, -3.0), (-16.0, -2.0), (-16.0, -1.0), (-16.0, 0.0), (-16.0, 1.0), (-16.0, 2.0), (-16.0, 3.0), (-16.0, 4.0), (-15.0, 4.0), (-15.0, 3.0), (-15.0, 2.0), (-15.0, 1.0), (-15.0, 0.0), (-15.0, -1.0), (-15.0, -2.0), (-15.0, -3.0), (-15.0, -4.0), (-15.0, -5.0), (-14.0, -5.0), (-14.0, -4.0), (-14.0, -3.0), (-14.0, -2.0), (-14.0, -1.0), (-14.0, 0.0), (-14.0, 1.0), (-14.0, 2.0), (-14.0, 3.0), (-14.0, 4.0), (-13.0, 4.0), (-13.0, 3.0), (-13.0, 2.0), (-13.0, 1.0), (-13.0, 0.0), (-13.0, -1.0), (-13.0, -2.0), (-13.0, -3.0), (-13.0, -4.0), (-13.0, -5.0), (-12.0, -5.0), (-12.0, -4.0), (-12.0, -3.0), (-12.0, -2.0), (-12.0, -1.0), (-12.0, 0.0), (-12.0, 1.0), (-12.0, 2.0), (-12.0, 3.0), (-12.0, 4.0), (-11.0, 4.0), (-11.0, 3.0), (-11.0, 2.0), (-11.0, 1.0), (-11.0, 0.0), (-11.0, -1.0), (-11.0, -2.0), (-11.0, -3.0), (-11.0, -4.0), (-11.0, -5.0), (-10.0, -5.0), (-10.0, -4.0), (-10.0, -3.0), (-10.0, -2.0), (-10.0, -1.0), (-10.0, 0.0), (-10.0, 1.0), (-10.0, 2.0), (-10.0, 3.0), (-10.0, 4.0), (-9.0, 4.0), (-9.0, 3.0), (-9.0, 2.0), (-9.0, 1.0), (-9.0, 0.0), (-9.0, -1.0), (-9.0, -2.0), (-9.0, -3.0), (-9.0, -4.0), (-9.0, -5.0), (-8.0, -5.0), (-8.0, -4.0), (-8.0, -3.0), (-8.0, -2.0), (-8.0, -1.0), (-8.0, 0.0), (-8.0, 1.0), (-8.0, 2.0), (-8.0, 3.0), (-8.0, 4.0), (-7.0, 4.0), (-7.0, 3.0), (-7.0, 2.0), (-7.0, 1.0), (-7.0, 0.0), (-7.0, -1.0), (-7.0, -2.0), (-7.0, -3.0), (-7.0, -4.0), (-7.0, -5.0), (-6.0, -5.0), (-6.0, -4.0), (-6.0, -3.0), (-6.0, -2.0), (-6.0, -1.0), (-6.0, 0.0), (-6.0, 1.0), (-6.0, 2.0), (-6.0, 3.0), (-6.0, 4.0), (-5.0, 4.0), (-5.0, 3.0), (-5.0, 2.0), (-5.0, 1.0), (-5.0, 0.0), (-5.0, -1.0), (-5.0, -2.0), (-5.0, -3.0), (-5.0, -4.0), (-5.0, -5.0), (-4.0, -5.0), (-4.0, -4.0), (-4.0, -3.0), (-4.0, -2.0), (-4.0, -1.0), (-4.0, 0.0), (-4.0, 1.0), (-4.0, 2.0), (-4.0, 3.0), (-4.0, 4.0), (-3.0, 4.0), (-3.0, 3.0), (-3.0, 2.0), (-3.0, 1.0), (-3.0, 0.0), (-3.0, -1.0), (-3.0, -2.0), (-3.0, -3.0), (-3.0, -4.0), (-3.0, -5.0), (-2.0, -5.0), (-2.0, -4.0), (-2.0, -3.0), (-2.0, -2.0), (-2.0, -1.0), (-2.0, 0.0), (-2.0, 1.0), (-2.0, 2.0), (-2.0, 3.0), (-2.0, 4.0), (-1.0, 4.0), (-1.0, 3.0), (-1.0, 2.0), (-1.0, 1.0), (-1.0, 0.0), (-1.0, -1.0), (-1.0, -2.0), (-1.0, -3.0), (-1.0, -4.0), (-1.0, -5.0), (0.0, -5.0), (0.0, -4.0), (0.0, -3.0), (0.0, -2.0), (0.0, -1.0), (0.0, 0.0), (0.0, 1.0), (0.0, 2.0), (0.0, 3.0), (0.0, 4.0), (1.0, 4.0), (1.0, 3.0), (1.0, 2.0), (1.0, 1.0), (1.0, 0.0), (1.0, -1.0), (1.0, -2.0), (1.0, -3.0), (1.0, -4.0), (1.0, -5.0), (2.0, -5.0), (2.0, -4.0), (2.0, -3.0), (2.0, -2.0), (2.0, -1.0), (2.0, 0.0), (2.0, 1.0), (2.0, 2.0), (2.0, 3.0), (2.0, 4.0), (3.0, 4.0), (3.0, 3.0), (3.0, 2.0), (3.0, 1.0), (3.0, 0.0), (3.0, -1.0), (3.0, -2.0), (3.0, -3.0), (3.0, -4.0), (3.0, -5.0), (4.0, -5.0), (4.0, -4.0), (4.0, -3.0), (4.0, -2.0), (4.0, -1.0), (4.0, 0.0), (4.0, 1.0), (4.0, 2.0), (4.0, 3.0), (4.0, 4.0), (5.0, 4.0), (5.0, 3.0), (5.0, 2.0), (5.0, 1.0), (5.0, 0.0), (5.0, -1.0), (5.0, -2.0), (5.0, -3.0), (5.0, -4.0), (5.0, -5.0), (6.0, -5.0), (6.0, -4.0), (6.0, -3.0), (6.0, -2.0), (6.0, -1.0), (6.0, 0.0), (6.0, 1.0), (6.0, 2.0), (6.0, 3.0), (6.0, 4.0), (7.0, 4.0), (7.0, 3.0), (7.0, 2.0), (7.0, 1.0), (7.0, 0.0), (7.0, -1.0), (7.0, -2.0), (7.0, -3.0), (7.0, -4.0), (7.0, -5.0), (8.0, -5.0), (8.0, -4.0), (8.0, -3.0), (8.0, -2.0), (8.0, -1.0), (8.0, 0.0), (8.0, 1.0), (8.0, 2.0), (8.0, 3.0), (8.0, 4.0), (9.0, 4.0), (9.0, 3.0), (9.0, 2.0), (9.0, 1.0), (9.0, 0.0), (9.0, -1.0), (9.0, -2.0), (9.0, -3.0), (9.0, -4.0), (9.0, -5.0), (10.0, -5.0), (10.0, -4.0), (10.0, -3.0), (10.0, -2.0), (10.0, -1.0), (10.0, 0.0), (10.0, 1.0), (10.0, 2.0), (10.0, 3.0), (10.0, 4.0), (11.0, 4.0), (11.0, 3.0), (11.0, 2.0), (11.0, 1.0), (11.0, 0.0), (11.0, -1.0), (11.0, -2.0), (11.0, -3.0), (11.0, -4.0), (11.0, -5.0), (12.0, -5.0), (12.0, -4.0), (12.0, -3.0), (12.0, -2.0), (12.0, -1.0), (12.0, 0.0), (12.0, 1.0), (12.0, 2.0), (12.0, 3.0), (12.0, 4.0), (13.0, 4.0), (13.0, 3.0), (13.0, 2.0), (13.0, 1.0), (13.0, 0.0), (13.0, -1.0), (13.0, -2.0), (13.0, -3.0), (13.0, -4.0), (13.0, -5.0), (14.0, -5.0), (14.0, -4.0), (14.0, -3.0), (14.0, -2.0), (14.0, -1.0), (14.0, 0.0), (14.0, 1.0), (14.0, 2.0), (14.0, 3.0), (14.0, 4.0), (15.0, 4.0), (15.0, 3.0), (15.0, 2.0), (15.0, 1.0), (15.0, 0.0), (15.0, -1.0), (15.0, -2.0), (15.0, -3.0), (15.0, -4.0), (15.0, -5.0), (16.0, -5.0), (16.0, -4.0), (16.0, -3.0), (16.0, -2.0), (16.0, -1.0), (16.0, 0.0), (16.0, 1.0), (16.0, 2.0), (16.0, 3.0), (16.0, 4.0), (17.0, 4.0), (17.0, 3.0), (17.0, 2.0), (17.0, 1.0), (17.0, 0.0), (17.0, -1.0), (17.0, -2.0), (17.0, -3.0), (17.0, -4.0), (17.0, -5.0), (18.0, -5.0), (18.0, -4.0), (18.0, -3.0), (18.0, -2.0), (18.0, -1.0), (18.0, 0.0), (18.0, 1.0), (18.0, 2.0), (18.0, 3.0), (18.0, 4.0), (19.0, 4.0), (19.0, 3.0), (19.0, 2.0), (19.0, 1.0), (19.0, 0.0), (19.0, -1.0), (19.0, -2.0), (19.0, -3.0), (19.0, -4.0), (19.0, -5.0), (20.0, -5.0), (20.0, -4.0), (20.0, -3.0), (20.0, -2.0), (20.0, -1.0), (20.0, 0.0), (20.0, 1.0), (20.0, 2.0), (20.0, 3.0), (20.0, 4.0), (21.0, 4.0), (21.0, 3.0), (21.0, 2.0), (21.0, 1.0), (21.0, 0.0), (21.0, -1.0), (21.0, -2.0), (21.0, -3.0), (21.0, -4.0), (21.0, -5.0), (22.0, -5.0), (22.0, -4.0), (22.0, -3.0), (22.0, -2.0), (22.0, -1.0), (22.0, 0.0), (22.0, 1.0), (22.0, 2.0), (22.0, 3.0), (22.0, 4.0), (23.0, 4.0), (23.0, 3.0), (23.0, 2.0), (23.0, 1.0), (23.0, 0.0), (23.0, -1.0), (23.0, -2.0), (23.0, -3.0), (23.0, -4.0), (23.0, -5.0), (24.0, -5.0), (24.0, -4.0), (24.0, -3.0), (24.0, -2.0), (24.0, -1.0), (24.0, 0.0), (24.0, 1.0), (24.0, 2.0), (24.0, 3.0), (24.0, 4.0), (25.0, 4.0), (25.0, 3.0), (25.0, 2.0), (25.0, 1.0), (25.0, 0.0), (25.0, -1.0), (25.0, -2.0), (25.0, -3.0), (25.0, -4.0), (25.0, -5.0)]
sequence = load_TSP_waypoints('TSp optimized waypoints.txt',robot_name)
print('sequence ',sequence)
_,victim_locations = load_dictionaries('victim_locations.txt')
#initialize the dictionary for victim detection
victim_detected_by_robot = {robot_name:[]}
detected_victims_location = {}

#-------------------------robot initilization---------------------------
prox = ['RCPS3','LCPS3','RPS3','LPS3','RPS3']
pio2 = pioneer('PioneerP3DX3', 'rightMotor3', 'leftMotor3', prox, 32000)


pio2.Initialization(False)
robot_position = pio2.robot_position()


"""----------------------------------Create and set up the server---------------------------------"""
host = "127.0.0.4"
port = 42001
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))



"""---------------------------------------------------------------------------------------------------"""


def coverage_path_planning(sequence):
    global robot_position
    for i in range(len(sequence)):

        try:
            status,robot_position = func_timeout(30, pio2.move_p2p, args=(0,sequence[i]))
            print(status)

            if (status == 1):
                print("reached at ",sequence[i])

        except FunctionTimedOut:
            pass
    return True


def maintain_communication(server_socket):
    """
    Function to handle robot communication with victims.

    Args:
        server_socket (socket.socket): Pre-initialized server socket.
    """
    global victim_detected_by_robot, detected_victims_location
    global robot_position
    victim_name = None  #initialize it to access from finally statement
    print("Robot communication thread started...")

    while True:
        # Listen for incoming connections
        server_socket.listen(5)
        print("Waiting for a victim to connect...")

        # Accept an incoming connection
        client_socket, addr = server_socket.accept()
        print(f"Connected to victim at {addr}")

        try:
            # Receive victim ID as the first message
            response = client_socket.recv(1024).decode()# Read victim ID (victim send in:'help_v1' format
            victim_name = response.split('_')[1]
            print(f"Victim ID received: {victim_name}")
            #print(type(victim_name))
            # Check if the victim ID is known and if the victim has already been recovered
            # if victim_id not in victim_positions:
            #     print(f"Unknown victim ID received: {victim_id}")
            #     client_socket.close()
            #     continue

            # Check if the victim has already been recovered by the robot
            if victim_name in victim_detected_by_robot[robot_name]:
                print(f"Victim {victim_name} has already been recovered by the robot. Closing communication.")
                client_socket.close()
                continue  # Move on to the next victim
            # check if the victim has already been rescued by other robot
            if is_victim_rescued('central_dictionary.txt',victim_name):
                print('already rescued and exist in dict')
                continue


            # Get the position of the victim (for checking of less or greater than 2m distance)
            print(victim_name)

            victim_position = victim_locations[victim_name]
            robot_pos = robot_position

            print('robot position',robot_pos,' victim position',victim_position)
            distance = math.sqrt((robot_pos[0]-victim_position[0])**2+(robot_pos[1]-victim_position[1])**2)
            print(f"Distance to {victim_name}: {distance:.2f} meters.")

            # If distance is greater than 2 meters, close the communication
            if distance > RFID_range:
                print(f"Victim {victim_name} is more than 2 meters away. Closing communication.")
                message = ' Connection rejection due to over distance'
                client_socket.sendall(message.encode())
                client_socket.close()
                continue  # Move on to the next victim

            # Maintain communication as long as the distance is <= 2 meters
            while distance <= RFID_range:
                print(f"Maintaining communication with victim {victim_name} (distance: {distance:.2f}m).")

                # Send "anyone" message to maintain communication
                message = "anyone_3"
                client_socket.sendall(message.encode())
                print(f"Sent message: {message}")

                # Receive the victim's response
                victim_loc = client_socket.recv(1024).decode()  # get victim location
                print(f"Received response of victim loc: {victim_loc} robot loc: {robot_position}")

                # Update the dictionaries with the recovered victim
                if victim_name not in victim_detected_by_robot[robot_name]:
                    victim_detected_by_robot[robot_name].append(victim_name)
                    detected_victims_location[victim_name] = victim_loc
                    print(f"Updated dictionaries: {victim_detected_by_robot}, {detected_victims_location}")
                    update_victim_data('central_dictionary.txt',robot_name,victim_name,victim_loc)
                    message = 'rescued'
                    client_socket.sendall(message.encode())
                    break

        # except Exception as e:
        #     print(f"Error during communication: {e}")

        finally:
            # Close client socket and continue to listen for another connection
            print(f"Communication with victim {victim_name} ended.")
            #write_data_to_file('central_dictionary.txt',victim_detected_by_robot,detected_victims_location)
            #update_victim_data('central_dictionary.txt',robot_name,victim_name,victim_loc)
            client_socket.close()

        # Optional: Add a sleep or break condition if needed
        time.sleep(0.01)  # Add a small delay between communication rounds

    # Optionally, you can add server shutdown logic if needed outside the while loop
    server_socket.close()
    print("Robot communication thread terminated.")

# Shared event to signal the communication thread
stop_communication_event = threading.Event()

def main(sequence):
    path_planning_thread = threading.Thread(target=coverage_path_planning, args=(sequence,))
    communication_thread = threading.Thread(target=maintain_communication,args=(server_socket,))

    # Start the threads
    path_planning_thread.start()
    communication_thread.start()

    # Wait for both threads to complete
    path_planning_thread.join()

    sim_time = pio2.get_current_simulation_time()
    hours = math.floor(sim_time / 3600000)
    minutes = math.floor((sim_time % 3600000) / 60000)
    seconds = math.floor((sim_time  % 60000) / 1000)
    # print the result
    print(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    communication_thread.join()

    print("All threads have completed.")
    return 0

if __name__ == "__main__":
    main(sequence)

#stop the robot
pio2.set_velocity(0,0)
time.sleep(0.5)

# calculate the simulation time in hours, minutes, and seconds

sim.simxFinish(pio2.clientID)



