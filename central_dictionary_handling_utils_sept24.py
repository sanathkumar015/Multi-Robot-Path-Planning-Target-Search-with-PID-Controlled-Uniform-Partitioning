def clear_text_file(file_path):
    #clear central dictionary
    with open(file_path, 'w') as file:
        file.write('')

def save_dictionaries(filename, detected_victims, victim_locations):
    if detected_victims == None:
        with open(filename, 'w') as file:
            file.write(f"detected_victims = {detected_victims}\n")
            file.write(f"victim_locations = {victim_locations}\n")
    elif detected_victims == 'TSP':
         with open(filename, 'w') as file:
            file.write(f"TSP_path = {victim_locations}\n")
    else:
        with open(filename, 'w') as file:
            file.write(f"detected_victims = {detected_victims}\n")
            file.write(f"victim_locations = {victim_locations}\n")

def load_TSP_waypoints(filename,robot_name):
    try:
        with open(filename, 'r') as file:
            content = file.read()


            # If the file is empty, return empty dictionaries
            if not content:
                return {}, {}

              # Read the entire file content
            # Extracting the dictionary part from the content and evaluating it
            dictionary_str = content.split(' = ')[1]  # Get the part after ' = '
            robot_number = int(robot_name[-1])
            dictionary = eval(dictionary_str)
            return dictionary[robot_number]['grid_points']  # Evaluate the string to a dictionary



    except (FileNotFoundError, IndexError):
        # If the file doesn't exist or there's an index error (in case of partial content), return empty dictionaries
        return {}, {}

def load_dictionaries(filename):
    try:
        with open(filename, 'r') as file:
            content = file.read().strip()

            # If the file is empty, return empty dictionaries
            if not content:
                return {}, {}

            # Otherwise, parse the content into Python objects (dictionaries)
            detected_victims = eval(content.splitlines()[0].split(' = ')[1])
            victim_locations = eval(content.splitlines()[1].split(' = ')[1])
        return detected_victims, victim_locations
    except (FileNotFoundError, IndexError):
        # If the file doesn't exist or there's an index error (in case of partial content), return empty dictionaries
        return {}, {}

def update_victim_data(filename, robot_name, victim_name, victim_location):
    # Load current data
    detected_victims, victim_locations = load_dictionaries(filename)

    # Update detected victims for the robot
    if robot_name in detected_victims:
        detected_victims[robot_name].append(victim_name)
    else:
        detected_victims[robot_name] = [victim_name]

    # Update victim locations
    victim_locations[victim_name] = tuple(victim_location)

    # Save updated data
    save_dictionaries(filename, detected_victims, victim_locations)


def is_victim_rescued(filename, victim_name):
    # Load current data
    detected_victims, _ = load_dictionaries(filename)

    # Check if the victim has been rescued by any robot
    for victims in detected_victims.values():
        if victim_name in victims:
            return True
    return False
