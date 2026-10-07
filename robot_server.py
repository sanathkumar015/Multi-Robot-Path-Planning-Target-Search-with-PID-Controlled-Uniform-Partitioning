# robot_server.py
import socket

# robot_server.py
import socket
import threading
import time

# Robot's initial state
robot_name = "Robot1"
recovered_victims = {}  # Dictionary to track recovered victims and their positions
a = time.time()
# Function to handle responses from each victim
def handle_victim_response(client_socket, addr):
    while True:
        try:
            # Receive victim's response
            response = client_socket.recv(1024).decode()
            if not response:
                break

            # Parse the victim's response message, e.g., "help_V1,10,15"
            message, x, y = response.split(',')
            victim_name = message.split('_')[1]  # Extract victim ID (e.g., V1 from help_V1)
            x, y = float(x), float(y)  # Convert coordinates to float

            # Update dictionary with victim's name and location
            recovered_victims[victim_name] = (x, y)
            print(f"Recovered {victim_name} at location ({x}, {y})")

        except Exception as e:
            print(f"Error handling victim response from {addr}: {e}")
            break

    # Close the client socket after handling the victim
    client_socket.close()
    print(f"Victim at {addr} disconnected.")

# Function to broadcast "anyone" message and handle victim responses
def run_robot_server(host='127.0.0.3', port=65432):
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Robot server listening on {host}:{port}...")

    # Continuously broadcast "anyone" message and listen for responses
    while True:
        print("Broadcasting 'anyone' message...")
        # Accept a new connection (victim response)
        client_socket, addr = server_socket.accept()
        print(f"Connected to victim at {addr}")

        # Handle victim response in a new thread
        threading.Thread(target=handle_victim_response, args=(client_socket, addr)).start()

        # Sleep for a while before the next broadcast (simulate continuous broadcasting)
        time.sleep(2)

# Main execution
run_robot_server()


