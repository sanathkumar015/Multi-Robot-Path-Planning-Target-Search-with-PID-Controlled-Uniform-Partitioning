from Multi_Robot_area_allocation_utilities_Sept_24_v2 import *
from TSP_optimization_utils_sept_24 import *
from central_dictionary_handling_utils_sept24 import *
import time
import matplotlib.pyplot as plt
# Enable interactive mode of plt for real time plotting of calculted  area and io
plt.ion()
from shapely.geometry import Polygon



#if take long to converge change initial_slope (at two places)
# take different kp, kd, ki

#polygon_coordinate = [[-25,25],[-25,-25],[25,-25],[25,25]] #main polygon setup 1
polygon_coordinate = [[-25,20],[-25,-20],[-10,-25],[10,-20],[25,-10],[25,10],[10,25],[0,25]]  #main polygon setup 02

edge_equations = polygon_edge_equations(polygon_coordinate)

#robot_position = np.array([[-25,15],[-25,5],[-25,0],[-25,-5],[-25,-22]]) # For PID tuning case
#robot_position = np.array([[-25,20],[-25,10],[-25,0],[-25,-10],[-25,-20]]) # robot position 1 for polygon setup 1
#robot_position = np.array([[-25,15],[-25,0],[-25,-15],[-15,-25],[15,-25]]) # robot position 2 for polygon setup 1

#robot_position = np.array([[-25,15],[-25,0],[-25,-15],[-17.5,-22.5],[0,-22.5]]) # robot position 1 for polygon setup 2
robot_position = np.array([[-25,15],[-25,0],[-25,-15],[-17.5,-22.5],[0,-22.5],[17.5,-15]]) # robot position 2 for polygon setup 2


#draw_main_polygon_with_robots(polygon_coordinate,list(robot_position))


midpoints = get_initial_point_for_area_allocation(polygon_coordinate,robot_position)
print('Initial base points for area division (midpoints): ',midpoints)


# #-------------------------------Iteratively solve for equal area allocation-----------------------


total_area = calculate_polygon_area(polygon_coordinate)
target_area = total_area / len(robot_position)
area_tol = 1 # Area tolerance in m^2
area = []
print('Total area:', total_area, 'Total Robots: ',len(robot_position), ' Per robot allocated area: ', target_area)
print('\n')
sp.symbols('x y')
initial_slope = 18.39 #3

#kp, kd,ki = 0.09,0,0

#--------------------------------------------
#kp, kd,ki = 0.058,0.001,0.0001
#kp,kd,ki = 0.009,0.005,0.0001 #last value 2
#kp,kd,ki = 0.007,0.005,0.0005
#-------------------------------------------
#kp,kd,ki = 0.058,0.0005,0.0001               #last value
kp,kd,ki = 0.05,0.001,0.0002 #fina value for paper
#kp,kd,ki = 0.05,0.00001,0.0002




integral_error = 0
prev_line_solution_points  = []
required_vertices_for_area_calculation = []
main_solution_points = []
robot_polygons_after_area_division = []
prev_area_error = 0
current_mother_polygon = polygon_coordinate.copy()


                                    ###### real time plotting of area and iteration
# Create figure and axis
fig, ax = plt.subplots()
line, = ax.plot([], [], 'b-o',markersize=4, linewidth = 1, label="Area of sub-polygons" +r'($m^2$)')  # Line plot for (x, y)
constant_line = ax.axhline(y=target_area, color='r', linestyle='--', label="Target Area: "+str(round(target_area,0))+r' $m^2$')  # Constant line at y=50
ax.set_xlabel("X")
ax.set_ylabel("Y")
plt.title("Area of sub-polygon with iterations ")
ax.legend()

all_current_area = [] #for plotting of calculated area vs in each iteration
all_slope = []
iterations = []
percentage_area_error = []
iteration_tracker = 0

for i in range(len(midpoints)):
    print('trying for midpoint ',midpoints[i])
    print('\n')
    #area.append()

    for j in range(500):
        iteration_tracker = iteration_tracker + 1
        iterations.append(iteration_tracker) #keep track of total iteration for a experimental setup
        all_slope.append(initial_slope)
        eq = line_equation_from_point_slope(midpoints[i], math.tan(math.radians(initial_slope)))
        #print('bisector equation: ', eq)
        current_solution_points = solve_bisector_with_edges(eq, edge_equations, current_mother_polygon)
        #print('current mother polygon ',current_mother_polygon)
        #print('current_solution_points',current_solution_points)
        curr_soln_left_points, curr_soln_right_points = separate_points(current_solution_points, current_mother_polygon)
        robot_polygon_vertices = curr_soln_left_points + current_solution_points
        #print(curr_soln_left_points,' !', curr_soln_right_points)

        #print('robot_polygon_vertices ',robot_polygon_vertices)
        current_area = calculate_polygon_area(robot_polygon_vertices)
        all_current_area.append(current_area)

         # Update the real time plot
        line.set_xdata(iterations)
        line.set_ydata(all_current_area)
        ax.relim()  # Adjust the limits
        ax.autoscale_view()  # Autoscale to fit the data
        plt.pause(0.0005)  # Pause for the plot to update


        line.

        print('     Current assigned area:', current_area)
        if current_area == 0:
            #print('khatam')
            #initial_slope = -initial_slope
            pass
        area_error = current_area - target_area
        integral_error = integral_error + area_error
        #print('current error',area_error)
        #print('integral error ',integral_error)

        #print('prev error',prev_area_error)
        if abs(area_error) >= area_tol:
            #print('     Current area is not equal to equal area')
            #print('\n')
            initial_slope = slope_generator_PID_controller(area_error, prev_area_error, integral_error,initial_slope, kp, kd,ki,area_tol)
            #initial_slope = slope_generator_PD_controller(area_error,prev_error,initial_slope,kp,kd)
            #print('adjusted slope ',initial_slope)

            prev_area_error = area_error
            area.append(round(current_area,3))
        else:
            print('     Eureka! at iteration ',j+1)
            percentage_area_error.append(round(abs(area_error)*100/target_area,3))
            #print('     current solution points: ',current_solution_points)
            #print('     Iteration needed for midpoint ',i+1,' is', j+1)
            #print('-----------------------------------------------------------')
            prev_line_solution_points = current_solution_points
            main_solution_points.append(prev_line_solution_points)
            robot_polygons_after_area_division.append(robot_polygon_vertices)
            current_mother_polygon =  [item for item in current_mother_polygon if item not in curr_soln_left_points] #delet the left vertices of current polygon
            current_mother_polygon = [current_solution_points[0]] + current_mother_polygon + [current_solution_points [1]]
            new_line = line_equation_from_points(current_solution_points[0],current_solution_points[1])
            #edge_equations.append(new_line)
            edge_equations = polygon_edge_equations(current_mother_polygon)
            #print(' edge eqns ',edge_equations)
            #print('cmp: ' ,current_mother_polygon)
            #area[i].append(current_area)
            #prev_area_error = 0
            #integral_error = 0
            prev_area_error = area_error
            #initial_slope = 1.3* initial_slope
            area.append(round(current_area,3))
            break
plt.ioff()
plt.savefig('PID tuning.png', dpi=300, bbox_inches='tight', pad_inches=0.1)
plt.show()

percentage_area_error.append(round(abs(calculate_polygon_area(current_mother_polygon)-target_area)*100/target_area,3))
print('area of last polygom',calculate_polygon_area(current_mother_polygon))
print('percentage error: ', percentage_area_error)
print('avg percentage error: ',np.mean(percentage_area_error))

#time.sleep(5)
# #append the last polygon, which is automatically balanced
robot_polygons_after_area_division.append(current_mother_polygon)
print(robot_polygons_after_area_division)
#----------------------------------------------------------------------------------------------
# Draw schematics (assigned polygons with boundary line)
#draw_polygon_with_lines (polygon_coordinate,main_solution_points,robot_position)

#------------------------------------------------------------------------------------------------
# Correcting the assigned polygon by order
correct_polygon_order_for_each_robot = []


for i, polygon_points in enumerate(robot_polygons_after_area_division):
    # Convert to numpy array
    polygon_points = np.array(polygon_points)

    # Compute the convex hull to order points
    hull = ConvexHull(polygon_points)

    # Extract the ordered points
    ordered_points = polygon_points[hull.vertices]
    correct_polygon_order_for_each_robot.append(ordered_points)

#----------------------------------------------------------------------------------------------------
# #-------------------------------- Plot all polygons with color fill-----------------------

#print(" Vertices of assigned polygons")
#print(correct_polygon_order_for_each_robot)
plot_polygons_with_color_fill(correct_polygon_order_for_each_robot,robot_position)

#----------------------------- generate grid points of mother polygon---------------------------
data_dict = {}
mother_polygon_grid_points = generate_grid_in_polygon(polygon_coordinate,cell_size=1)
# #----------------------------make child poygon,using the result of area division (correct_polygon_order_for_each_robot)------------------
#
child_polygons = []
for i in range(len(correct_polygon_order_for_each_robot)):
    child_polygons.append(Polygon(correct_polygon_order_for_each_robot[i]))

#-----------------------------------------------------------------------
#--------------------------------- Assign mother grid points to child polygon-----------------------------------
# -----------------------------assigning grid points and making data dict. ----------------------------
#---------------------------with each robot ID as a key, position and assigned grid array as two value-----------------------
# ---------------------- assigning grid points to child polygons

# Define the mother polygon
mother_polygon = Polygon(polygon_coordinate)

# Define the points
points = mother_polygon_grid_points.copy()

# Assign the points to the child polygons
child_points = assign_points_to_polygons(mother_polygon, child_polygons, points)

##------------------------------ Making data dictionary [Unoptimized - No TSP]---------------------------------
print('Total Grid points of mother polygon: ',len(mother_polygon_grid_points))
for i in range (len(correct_polygon_order_for_each_robot)):

    polygon_coords = correct_polygon_order_for_each_robot[i]  # Irregular convex polygon coordinates
    grid_points = child_points[i]
    print('Total Grid points for robot ',i,' is: ',len(grid_points))

    data_dict[i+1] = {'robot_position':robot_position[i],'grid_points':grid_points}

#----------------------- Print unoptimized Data dictionary--------------------------
print('-------------printing Unoptimized waypoints----------------------------------------')
print('\n')
for i in range(len(data_dict)):
        print('Grid points for robot ',i,': robot_position', data_dict[i+1]['robot_position'])
        print('Grid points: ', data_dict[i+1]['grid_points'])

#--------------------------------------------Print TSP optimized Path Data dictionary--------------------------------------------------
optimized_data_dict = {}
print('\n')
print('TSP Optimization')
print('-------------printing optimized waypoints----------------------------------------')
print('\n')
for i in range(len(data_dict)):
    path,cost = tsp(list(data_dict[i+1]['robot_position']),data_dict[i+1]['grid_points'],'e')
    optimized_data_dict[i+1] = {'robot_position':list(robot_position[i]),'grid_points':path}
    total_distance = calculate_total_distance(path)
    print('total length of path of robot ',i+1,'& total distance: ',total_distance )
    print('Optimized Grid points for robot ',i,': robot_position', optimized_data_dict[i+1]['robot_position'])
    print('Grid points: ', optimized_data_dict[i+1]['grid_points'])
    print('\n')



#---------------------------------draw optimized path--------------------------
#save figure with filename
#draw_optimized_paths(optimized_data_dict,polygon_coordinate,'filename')

draw_optimized_paths(optimized_data_dict,polygon_coordinate)





#Save TSP optimized waypoint in a dictionary file

save_dictionaries('TSp optimized waypoints.txt','TSP',optimized_data_dict)


                                        #--------------SAVE PID tuning Data
def save_pid_tuning_data(file_name, kp, ki, kd, setpoints, areas):
    """
    Saves PID tuning data to a text file. If the file already exists, it appends the new data.

    Args:
        file_name (str): The name of the file to save the data.
        kp (float): Proportional gain.
        ki (float): Integral gain.
        kd (float): Derivative gain.
        setpoints (list): List of setpoints (single value expected).
        areas (list): List of area values corresponding to the setpoint.
    """
    # Prepare the data line to be written
    setpoint_value = setpoints  # Get the single setpoint value
    areas_str = area # Convert area values to a comma-separated string

    data_line = f"data1 = 'Kp': {kp}, 'Ki': {ki}, 'Kd': {kd}, 'Setpoint': {setpoint_value}, 'Areas': [{areas_str}]\n"


    # Open the file in append mode
    with open(file_name, 'a') as file:
        file.write(data_line)

# Example usage
file_name = 'pid_tuning_data.txt'
save_pid_tuning_data(file_name,kp,ki,kd,target_area,area)

#print(area)



# Create a plot
fig, ax = plt.subplots(figsize=(20, 12))

# Plot the data
ax.plot(np.arange(1,iterations[-1]+1,1),all_current_area)
ax.plot(np.arange(1,iterations[-1]+1,1),all_slope)
ax.axhline(y=target_area, color='r', linestyle='--',label = 'Target area')

# Initialize the cursor (vertical and horizontal lines)
cursor_x = ax.axvline(x=0, color='red', linestyle='--')  # Vertical cursor line
cursor_y = ax.axhline(y=0, color='red', linestyle='--')  # Horizontal cursor line

# Display the text label for the cursor
cursor_text = ax.text(0.05, 0.95, '', transform=ax.transAxes, color='red', fontsize=12)

# Function to update the cursor position and label
def update_cursor(event):
    if event.inaxes != ax:
        return  # If mouse is outside the axes, do nothing

    # Update the position of the cursor lines
    cursor_x.set_xdata([event.xdata, event.xdata])
    cursor_y.set_ydata([event.ydata, event.ydata])

    # Update the cursor text with the x, y coordinates
    cursor_text.set_text(f'X: {event.xdata:.2f}, Y: {event.ydata:.2f}')

    # Redraw the figure to update the cursor position
    fig.canvas.draw()

# Connect the motion_notify_event to update the cursor
fig.canvas.mpl_connect('motion_notify_event', update_cursor)

# Add labels and legend
ax.set_xlabel('Iterations')
ax.set_ylabel('Area / Slope')
ax.legend()

# Display the plot
plt.show()


