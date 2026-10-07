from central_dictionary_handling_utils_sept24 import *
from robot_motion_communication_utils import *
import socket
import threading

#clear all files
clear_text_file('central_dictionary.txt') # keep track of detected victims and locations by each robot
clear_text_file('victim_locations.txt') #store all victim locations, to check distance less equal then RFID distance
print('Program started')
sim.simxFinish(-1)
ports = list(range(60000,75000,1000))   #ports start from 64000, ends at 74000, stepping 1000
total_victims = 15
victim_handles = []
victim_locations = {}
victim_names = ['V1','V2','V3','V4','V5','V6','V7','V8','V9','V10','V11','V12','V13','V14','V15']


robot_server_hosts = {'robot1':'127.0.0.2','robot2':'127.0.0.3','robot3':'127.0.0.4','robot4':'127.0.0.5','robot5':'127.0.0.6','robot6':'127.0.0.7'}
robot_ports = {'robot1':40000,'robot2':41001,'robot3':42001,'robot4':43000,'robot5':44000,'robot6':45000}

client_sockets = {}
#--------------------------victim initialization,-------------------
for i in range(total_victims):
    clientID = sim.simxStart('127.0.0.1', ports[i], True, True, 5000, 5)
    if clientID == -1:
        print("Connected Failed with victim, ",i+1)
    else:
        print("Connected Successfully")
    victim_handles.append(sim.simxGetObjectHandle(clientID,'/'+'V'+str(i+1), sim.simx_opmode_blocking)[1]) #Collect all victim handles
    _, position = sim.simxGetObjectPosition(clientID, victim_handles[i], -1, sim.simx_opmode_blocking)     #Get all victims positions
    val = [round(position[0], 3), round(position[1], 3)]
    victim_locations[victim_names[i]] = val
    client_sockets[victim_names[i]] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(victim_locations)
save_dictionaries('victim_locations.txt',None,victim_locations)





#---------------------------------------------------------------------


# def victim_communication(victim_name,victim_locations):
#
#     try:
#         while True:
#             key = random.choice(list(robot_server_hosts.keys()))
#             #server = '127.0.0.3'#robot_server_hosts[key]
#             #port =  41000 #robot_ports[key]
#             #key = 'robot5'
#             server = robot_server_hosts[key]
#             port = robot_ports[key]
# #
#
#             client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             client_socket.connect((server,port))
#
#             message = 'help_'+ victim_name
#             client_socket.sendall(message.encode('utf-8'))
#
#             # Wait for a 'anyone' response
#             response = client_socket.recv(1024).decode('utf-8')  # Buffer size of 1024 bytes
#             print(f"Client {victim_name} received response: {response}")
#             #print('response start with anyone or nor: ',response.startswith('anyone'))
#
#
#             if response.startswith('anyone'):
#
#                 message = str(victim_locations[victim_name])
#                 #print(message)
#                 client_socket.sendall((message.encode('utf-8')))
#
#                 response = client_socket.recv(1024).decode('utf-8')
#                 print(f"Client {victim_name} received response: {response}")
#
#                 if response.startswith('rescued'):
#                     del victim_locations[victim_name]
#                     victim_names.remove(victim_name)
#                     print('victim name and loc',victim_names,victim_locations)
#                     client_socket.close()
#                     print(f"Client {victim_name} is rescued by {key}")
#             break



    # except Exception as e:
    #     print(e)
    #     print(f"Client {victim_name} could not connect: {e}")
    #     time.sleep(1)

def victim_communication_2(victim_name, victim_locations):
    client_socket = None  # Initialize the socket outside the loop

    try:
        while True:
            try:
                # Randomly pick a robot server to communicate
                key = random.choice(list(robot_server_hosts.keys()))
                #server = '127.0.0.3'#robot_server_hosts[key]
                #port =  41000 #robot_ports[key]
                #key = 'robot3'
                server = robot_server_hosts[key]
                port = robot_ports[key]

                # Create and connect the socket
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((server, port))

                # Send the 'help' message with the victim name
                message = 'help_' + victim_name
                client_socket.sendall(message.encode('utf-8'))
                time.sleep(1)

                # Wait for the response
                response = client_socket.recv(1024).decode('utf-8')
                if len(response)>1 :
                    print(f"Client {victim_name} received response: {response} ")

                # If a robot responds with 'anyone', send the victim's location
                if response.startswith('anyone'):
                    robot_connected = response.split('_')[-1]
                    print(victim_name,' is connected to Robot',robot_connected)
                    message = str(victim_locations[victim_name])
                    client_socket.sendall(message.encode('utf-8'))
                    time.sleep(1)
                    # Wait for the 'rescued' response
                    response = client_socket.recv(1024).decode('utf-8')
                    print(f"Client {victim_name} received response: {response}")

                    # If the victim is rescued, exit the loop and close the connection
                    if response.startswith('rescued'):
                        del victim_locations[victim_name]  # Remove the rescued victim from the locations
                        victim_names.remove(victim_name)  # Remove the victim from the list of active victims
                        print(f"Victim {victim_name} rescued by {key}")
                        break  # Exit the loop, meaning the victim has been rescued

            except Exception as e:
                # Handle connection failure or other exceptions
                print(f"Error: {e}")
                print(f"Retrying communication for {victim_name}...")
                #time.sleep(random.randint(1,10))  # Wait for a short period before retrying

            finally:
                # Close the socket if it was successfully created
                if client_socket:
                    client_socket.close()
                    client_socket = None  # Reset the socket for the next retry

    except Exception as final_exception:
        print(f"Final error for victim {victim_name}: {final_exception}")

    finally:
        # Final cleanup or logging if needed
        print(f"Communication for victim {victim_name} has ended")

def main():
    # Create a list to hold the threads for each victim
    threads = []
    global victim_names,victim_locations


    # Start a separate thread for each victim
#    victim_names = ['V6']#'V2','V3'],'V4','V5','V6']

    for victim_name in victim_names: # create thread as much as victim
        print('victim name: ',victim_name)
        thread = threading.Thread(target=victim_communication_2, args=(victim_name,victim_locations))
        #time.sleep(1)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete (optional)
    for thread in threads:
        thread.join()

# Run the main function
if __name__ == "__main__":
    main()



