import math
import time
from robot_motion_communication_utils import *
import socket
import threading
from central_dictionary_handling_utils_sept24 import*

running = True
robot_position = [-25,10]
robot_name = 'robot2'
RFID_range = 2
#copy the grid point from the result of Multi Robot Area Allocation & TSP opt- Main file - Sept 24 file
sequence = load_TSP_waypoints('TSp optimized waypoints.txt',robot_name)
print('sequence ',sequence)
_,victim_locations = load_dictionaries('victim_locations.txt')

#initialize the dictionary for victim detection
victim_detected_by_robot = {robot_name:[]}
detected_victims_location = {}

#-------------------------robot initilization---------------------------
prox = ['RCPS2','LCPS2','RPS2','LPS2','RPS2']
pio2 = pioneer('PioneerP3DX2', 'rightMotor2', 'leftMotor2', prox, 30000)
pio2.Initialization(False)
robot_position = pio2.robot_position()
a = 0



"""----------------------------------Create and set up the server---------------------------------"""
host = "127.0.0.3"
port = 41000+1
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))



"""---------------------------------------------------------------------------------------------------"""

def coverage_path_planning(sequence):
    global robot_position
    for i in range(len(sequence)):

        try:
            status,robot_position = func_timeout(30, pio2.move_p2p, args=(0,sequence[i]))
            #print(status)
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
                continue


            # Get the position of the victim (for checking of less or greater than 2m distance)
            print(victim_name)
            victim_position = victim_locations[victim_name]
            robot_pos = robot_position
            distance = math.sqrt((robot_pos[0]-victim_position[0])**2+(robot_pos[1]-victim_position[1])**2)
            print(f"Distance to {victim_name}: {distance:.2f} meters.")

            # If distance is greater than 2 meters, close the communication
            if distance > RFID_range:
                print(f"Victim {victim_name} is more than 2 meters away. Closing communication.")
                message = 'Connection rejection due to over distance'
                client_socket.sendall(message.encode())
                client_socket.close()
                continue  # Move on to the next victim

            # Maintain communication as long as the distance is <= 2 meters
            while distance <= RFID_range:
                print(f"Maintaining communication with victim {victim_name} (distance: {distance:.2f}m).")

                # Send "anyone" message to maintain communication
                message = "anyone_2"
                client_socket.sendall(message.encode())
                print(f"Sent message: {message}")

                # Receive the victim's response
                victim_loc = client_socket.recv(1024).decode()  # get victim location
                print(f"Received response of victim loc: {victim_loc}")

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
   # path_planning_thread = threading.Thread(target=coverage_path_planning, args=(sequence,))
    communication_thread = threading.Thread(target=maintain_communication,args=(server_socket,))

    # Start the threads
   # path_planning_thread.start()
    communication_thread.start()

    # Wait for both threads to complete
   # path_planning_thread.join()
    communication_thread.join()

    print("All threads have completed.")
    return 0

if __name__ == "__main__":
   main(sequence)


#stop the robot
pio2.set_velocity(0,0)
time.sleep(0.5)

# calculate the simulation time in hours, minutes, and seconds
sim_time = pio2.get_current_simulation_time()

hours = math.floor(sim_time / 3600000)
minutes = math.floor((sim_time % 3600000) / 60000)
seconds = math.floor((sim_time  % 60000) / 1000)

# print the result
print(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
sim.simxFinish(pio2.clientID)












# detected_victim = None
# detected_victim_list = []
# pause_coverage = 0
# duplicate = 1
# kk = 0
# victim_location = {}
# waypoint = []


# for i in range(20):
#     msg = pio2.send_message('hello')
#     print(msg)

# while True:
#     waypoint_counter = 0
#     total_waypoints = len(sequence)
#     while waypoint_counter < total_waypoints:

#print(pio2.victim)

# j = 0
# while True:
#     detected_victim = pio2.victim_detection_2()
#     print("detected victim ",detected_victim)
#     j = j + 1
#     if j==1000:
#         break
# for i in range(100):
#     v = pio2.send_message('anyone?')
#     print(v)
#     time.sleep(0.01)
#     msg = pio2.receive_message()
#    # time.sleep(0.05)
#     print('message received by robot ',msg)
# while True:
#     detected_victim = pio2.victim_detection_2()
#     print("detected victim ",detected_victim)
#     counter = 0
#     while counter < len(sequence):
#         print("counter ",counter)
#         detected_victim = pio2.victim_detection_2()
#         print("detected victim ",detected_victim)
#
#         if (detected_victim!= None):
#             kk = 'v'+detected_victim
#             if kk not in detected_victim_list:
#                 duplicate = 0
#             else :
#                 duplicate = 1
#
#         if ((detected_victim == None) or duplicate == 1 ):
#             try:
#                 print("moving to: ",sequence[counter]," point")
#                 #status = self.move_p2p(0,i)
#                 waypoint.append(sequence[counter])
#                 status = func_timeout(55, pio2.move_p2p, args=(0,sequence[counter]))
#                 if (status == 1):
#                     print("reached at target")
#                 counter = counter + 1
#             except FunctionTimedOut:
#                     print ( "timeout. new target selected")
#                     counter = counter + 1
#                     pass
#         else:
#             print("v"+detected_victim," is detected")
#             if(check_key_in_file('victim_list.txt','v'+detected_victim)):
#                 print("some one has rescued it")
#                 detected_victim_list.append('v'+detected_victim)
#             else:
#                 detected_victim_list.append('v'+detected_victim)
#                 pos = pio2.get_victim_pos(detected_victim)
#                 pos = [pos[0]-0.3,pos[1]-0.3]
#                 waypoint.append(pos)
#                 try:
#                     status = func_timeout(55, pio2.move_p2p, args=(0,pos))
#
#                 except FunctionTimedOut:
#                         print ( "timeout. new target selected")
#                         victim_location.update({'v'+detected_victim : pos})
#
#                         pass
#                 victim_location.update({'v'+detected_victim : pos})
#                 append_to_dictionary_file('victim_list.txt','v'+detected_victim,pos)
#
#     if (counter == len(sequence)):
#         print("program end")
#         pio2.set_velocity(0,0)
#         break
#
# print(waypoint)
# print(victim_location)
# print(pio2.robotHandle)
