import sympy as sp
import numpy as np
import math

from scipy.spatial.distance import cdist
from shapely.geometry import Point, Polygon
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt


###########################################################################################
def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
##############################################################################################
#---------------------------------# Area allocation helping functions--------------------------

#-------------------------------------------------------
def line_equation_from_points(point1, point2):
    """
    Given two points, return the equation of the straight line using SymPy.

    Parameters:
    - point1: A tuple (x1, y1), the first point on the line.
    - point2: A tuple (x2, y2), the second point on the line.

    Returns:
    - line_eq: The symbolic equation of the line.
    """
    # Define the variables
    x, y = sp.symbols('x y')

    # Extract coordinates from points
    x1, y1 = point1
    x2, y2 = point2

    # Calculate the slope (m)
    if x2 == x1:
        return sp.Eq(x,x1)

    if y2 == y1:
        return sp.Eq(y,y1)

    slope = (y2 - y1) / (x2 - x1)

    # Calculate the equation y = mx + b by finding the intercept (b)
    intercept = y1 - slope * x1

    # Form the line equation: y = mx + b
    line_eq = sp.Eq(y, round(slope,6) * x + round(intercept,6))

    return line_eq

def line_equation_from_point_slope(point,slope):
    x, y = sp.symbols('x y')

    # Assume the edge is horizontal (for simplicity), adjust the angle
    # For a horizontal edge, the perpendicular angle is the same as the input.
    # If the edge is vertical, adjust the angle as follows (relative to the x-axis):
    # Vertical edge -> Adjust theta by subtracting 90 to align with the x-axis
#      edge_orientation = "vertical"  # Change this to "vertical" for vertical edges

    x0 = round(point[0],3)
    y0 = round(point[1],3)




    # Equation of the line: y - y0 = m * (x - x0), rearranged to y = m * (x - x0) + y0
    line_eq = sp.Eq(y, slope * (x - x0) + y0)

    # Print the line equation
    #  print(f"Line equation: {line_eq}")
    return line_eq

def solve_simultaneous_eq(eq1, eq2):
    """
    Solves two simultaneous equations and returns the solution point.

    Parameters:
    - eq1: The first symbolic equation.
    - eq2: The second symbolic equation.

    Returns:
    - solution: A dictionary containing the solution for x and y.
    """
    # Define the variables
    x, y = sp.symbols('x y')

    # Solve the system of equations
    soln = sp.solve([eq1, eq2], (x, y))
    #print(soln)

    solution = []
    if soln:

        solution.append([round(float(soln[x]),4), round(float(soln[y]),4)])
        return solution

    return None #if no solution point return None
#---------------------------------------------------------------------

#-------------------------------Edge Equations from vertices------------
def polygon_edge_equations(polygon_points):
    """
    Given the coordinates of a polygon, return the equations of its edges.

    Parameters:
    - polygon_points: A list of tuples representing the vertices of the polygon.

    Returns:
    - edge_equations: A list of SymPy equations for the edges of the polygon.
    """
    edge_equations = []
    num_points = len(polygon_points)

    # Loop through each consecutive pair of points
    for i in range(num_points):
        point1 = polygon_points[i]
        point2 = polygon_points[(i + 1) % num_points]  # Wrap around to the first point

        # Get the line equation for the edge
        edge_eq = line_equation_from_points(point1, point2)

        # Append the equation to the list
        edge_equations.append(edge_eq)

    return edge_equations

#----------------------------------------------------------------------------

#---------------initial Line equation from point & angle for midpoints----------------------------
def line_equation_from_point_angle(point,angle,edge_orientation):
    x, y = sp.symbols('x y')

    # Assume the edge is horizontal (for simplicity), adjust the angle
    # For a horizontal edge, the perpendicular angle is the same as the input.
    # If the edge is vertical, adjust the angle as follows (relative to the x-axis):
    # Vertical edge -> Adjust theta by subtracting 90 to align with the x-axis
#      edge_orientation = "vertical"  # Change this to "vertical" for vertical edges
    theta = angle
    x0 = round(point[0],3)
    y0 = round(point[1],3)


    if edge_orientation == "vertical":  #considering the angle will be given with the left edge
        if theta>= 90:
            theta_adjusted = angle - 90 # Adjust the angle for vertical edge
        else:
            theta_adjusted = angle + 90
    else:
        theta_adjusted = theta  # No adjustment needed for horizontal edge

    # Convert angle to radians
    theta_rad = round(math.radians(theta_adjusted),4)

    # Calculate the slope (m) using the tangent of the adjusted angle
    if theta_adjusted == 90.00 or theta_adjusted == 270.0:
        # Special case: vertical line (undefined slope)
        line_eq = sp.Eq(x, x0)
    else:
        m = math.tan(theta_rad)

        # Equation of the line: y - y0 = m * (x - x0), rearranged to y = m * (x - x0) + y0
        line_eq = sp.Eq(y, m * (x - x0) + y0)

    # Print the line equation
  #  print(f"Line equation: {line_eq}")
    return line_eq

#-----------------------------------------------------------------------------


#-----------Solve the bisector line with all edge equation.(Excludes the solution point outside of polygon)----------

def solve_bisector_with_edges(bisector_eq,edge_equations,polygon_coords=None):
    #Algorithm:
    #Solve a bisector or any equation with four edge equation
    # if there is solution, print it (Remove None value)
    # check the the solution point is inside or on the polygon
    # exclude the solution point outside of polygon
    tolerance = 0.005
    soln = []
    for i, eq in enumerate(edge_equations):
        solution_point = solve_simultaneous_eq(bisector_eq,edge_equations[i])
        #print(solution_point)
        if solution_point is not None:
            soln.append(solution_point)


    # ----------Remove None value and Flattening
    soln = [item for item in soln if item is not None]
    soln = [[item for sublist in inner_list for item in sublist] for inner_list in soln]


  #  soln = [[round(x, 3) for x in pair] for pair in soln]


    #------------- if no solution point return False
    if len(soln) == 0:
        return False


    #---------------check solution point is outside of polygon
    # Create a polygon from the coordinates
    polygon = Polygon(polygon_coords)

    # List to store points inside the polygon
    points_inside = []

    # Iterate over each point
    #print('All points: ',soln)
    for point in soln:
        point_obj = Point(point)

        # Check if the point is inside or On the polygon
        #print(polygon_coords)
        #if polygon.contains(point_obj) or polygon.distance(point_obj) <= tolerance:
        if polygon.buffer(tolerance).contains(point_obj) or polygon.buffer(tolerance).intersects(point_obj):
           # print('check')
            points_inside.append(point)  # Add the point if it's inside or On the polygon

    #print(points_inside)


    #Keep all unique points only (#when the bisector intersect at intersection point at two edge, same solution occurs, effectively a point only)
    unique_points_inside = []
    for point in points_inside:
        if point not in unique_points_inside:
            unique_points_inside.append(point)



    if (len(unique_points_inside)>2):
        print('point inside: ',unique_points_inside)
        unique_points_inside.pop
        #raise ValueError("Solution points must be two points")


#     #when the bisector intersect at intersection point at two edge, same solution occurs, effectively a point only
#     if (points_inside[0]==points_inside[1]):
#         return [points_inside[0]]

    return unique_points_inside

#-----------------------------------------------------------------------------------


#-----------------### separate_points_relative_to_line---------------------------
#(if point is on_line consider it as a left side point)
#(i/p: base points(#2) & test points or polygon vertices)
#(o/p: separate list - > left side & right side points)
#left and right are side based on point sequence of base points given as inputs

def separate_points(base_points, test_points):
    left_points = []
    right_points = []

    if len(base_points)<2:  #if base line is empty return empty left and right list
        return  left_points, right_points

    # Extract base points
    point1 = base_points[0]
    point2 = base_points[1]



    # Calculate the coefficients of the line equation (Ax + By + C = 0)
    A = point2[1] - point1[1]  # y2 - y1
    B = point1[0] - point2[0]  # x1 - x2
    C = A * point1[0] + B * point1[1]  # Ax1 + By1

    # Iterate over each test point
    for point in test_points:
        # Calculate the position of the point relative to the line
        position = A * point[0] + B * point[1] - C

        if position > 0:
            right_points.append(point)  # Point is on the right side of the line
        else:
            left_points.append(point)   # Point is on the left side of the line

    return left_points, right_points
#-----------------------------------------------------------------------------


#--------------Calculate area of a polygon irrespective of point sequence.-----------------
def calculate_polygon_area(points):
    """
    Calculate the area of a polygon using Shapely, handling unordered and possibly invalid points
    by using Convex Hull to preprocess the points.

    :param points: List of tuples representing the coordinates of the vertices (x, y)
    :return: The area of the polygon
    """
    #print(points)
    if len(points) < 3:
        return 0
        #raise ValueError("A polygon must have at least 3 vertices")

    # Convert points to numpy array
    points_np = np.array(points)

    # Compute the convex hull
    hull = ConvexHull(points_np)

    # Get the ordered points of the convex hull
    ordered_points = [tuple(points_np[v]) for v in hull.vertices]

    # Create a Polygon object
    poly = Polygon(ordered_points)
    print(type(poly))

    # Check if the polygon is valid

    # Calculate and return the area
    return poly.area
#------------------------------------------------------------------------------


## ---------------------Generate required slop to correct the equal area division error -----------------
#using PD controller

def slope_generator_PD_controller(error,prev_error,theta,kp, kd):

    correction = kp * error + kd *(error - prev_error)
    theta = theta + correction
    return theta
#------------------------------------------------------------------------------------

def slope_generator_PID_controller(error,prev_error,integral_error,slope,kp, kd,ki,error_tol):

    if abs(error) < error_tol:
        return slope

    #integral_error = min(integral_error,800)
    correction = kp * error + kd * (error - prev_error) + ki *(integral_error)
   # print('PID correction: ',correction)
    slope = slope + correction


    return slope
#----------------
#--------------------------------------------------------------------------------------

def get_initial_point_for_area_allocation(polygon_coordinate,robot_position):

    #Get initial midpoints between two consecutive robot positions.(In This way,midpoints can be achieved that do not lie on any edges)
    # But my area division algo works on starting point(midpoints) lying on edge
    """
   context: Sometimes the mid point may not lies on robot edge. It happens when consecutive two bot stay on different side.
            In that case, to start area allocation I select the polygon vertex, in between those two robots


    Idea: to find any polygon vertices that lie between two robots by checking for a direction change of two consecutive robot position
    Input: Polygon coordinate: Vertices of area, given from top left corner
           Robot positions
    output: New midpoints
    """

    midpoints = []

    for i in range(len(robot_position) - 1):
        x1, y1 = robot_position[i]
        x2, y2 = robot_position[i+1]
        midpoint = ((x1 + x2) / 2), ((y1 + y2) / 2)
        midpoints.append(list(midpoint))
    print('midpoints without modification ',midpoints)
        #-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def are_parallel_new(v1, v2):

        """
        Function to check if two 2D vectors are parallel.

        Parameters:
        v1 (list): First vector [x1, y1].
        v2 (list): Second vector [x2, y2].

        Returns:
        bool: True if the vectors are parallel, False otherwise.
        """

        # Check using the cross product (if zero, vectors are parallel)
        cross_product = v1[0] * v2[1] - v1[1] * v2[0]

        # Return True if cross product is zero, meaning vectors are parallel
        return cross_product == 0
            # - - - - - - - - - - - - - - - - - - - - - - - - - - -- - - - - - -

    vertex = 0
    modified_midpoints = []
    for i in range(len(robot_position)-1):
        v0 = np.array(polygon_coordinate[vertex])
        r0 = np.array(robot_position[i])
        r1 = np.array(robot_position[i+1])

        result = are_parallel_new(v0 - r0,v0 - r1)

        if result:
            #print('1st case')
            modified_midpoints.append(midpoints[i])
        else:
            #print(' else case')
            modified_midpoints.append(polygon_coordinate[vertex+1])
            vertex = vertex + 1
        #print(modified_midpoints)

    return modified_midpoints



## ------------------------------------Plot schematics of assigned polygon--------------------------
def draw_polygon_with_lines(polygon_coords, connecting_lines,robot_position):
    # Convert polygon coordinates to a numpy array for easier handling
    polygon_coords = np.array(polygon_coords)

    # Plot the polygon
    plt.plot(np.round(polygon_coords[:, 0],3), np.round(polygon_coords[:, 1],3), 'bo-', label='Polygon')  # 'bo-' plots with blue dots and lines
    plt.plot(np.round(polygon_coords[[0,-1], 0],3), np.round(polygon_coords[[0,-1], 1],3), 'bo-', label='Polygon')  # draw line between last and 1st point


    plt.fill(polygon_coords[:, 0], polygon_coords[:, 1], 'b', alpha=0.2)  # Fill polygon with a transparent color
    for i, point in enumerate(polygon_coords):
        plt.text(round(point[0],3), round(point[1],3), f'{point}', fontsize=9, ha='right',color='red')

    # Plot the connecting lines
    for line in connecting_lines:
        line = np.array(line)
        plt.plot(np.round(line[:, 0],3), np.round(line[:, 1]), 'r-', label='Connecting Lines' if line[0][0] == connecting_lines[0][0][0] else "")

        for point in line:
            plt.text(round(point[0],3), round(point[1],3), f'{point}', fontsize=9, ha='right',color='red')


    # Set labels, title, and grid
    plt.title('Polygon with Connecting Lines')
    plt.xlabel('X')
    plt.ylabel('Y')
    #plt.grid(True)

    # Add legend and show plot
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fontsize=10, ncol=3)

    plt.plot(robot_position[:, 0], robot_position[:, 1], 'kx', markersize=15, markeredgewidth=2)
    plt.show()
#--------------------------------------- Draw main exploration area (without allocation) and robot positions


# def draw_main_polygon_with_robots(polygon_coords, robot_positions):
#     """
#     Draws a polygon with a light red fill and marks robot positions with an 'X' sign.
#
#     Args:
#         polygon_coords (list of tuples): List of (x, y) coordinates defining the polygon.
#         robot_positions (list of tuples): List of (x, y) coordinates of robot positions.
#     """
#     # Create a figure and axis
#     fig, ax = plt.subplots()
#
#     # Draw the polygon with light red fill
#     polygon = Polygon(polygon_coords, closed=True, edgecolor='black', facecolor='lightcoral', alpha=0.5)
#     ax.add_patch(polygon)
#
#     # Extract x and y coordinates of the polygon for axis limits
#     poly_x, poly_y = zip(*polygon_coords)
#
#     # Plot robot positions with 'X' marker
#     robot_x, robot_y = zip(*robot_positions)
#     ax.scatter(robot_x, robot_y, color='blue', marker='x', s=100, label='Robot Position')
#
#     # Set axis limits for better visualization
#     ax.set_xlim(min(poly_x) - 1, max(poly_x) + 1)
#     ax.set_ylim(min(poly_y) - 1, max(poly_y) + 1)
#
#     # Add labels and legend
#     ax.set_title('Polygon and Robot Positions')
#     ax.set_xlabel('X-axis')
#     ax.set_ylabel('Y-axis')
#     ax.legend()
#
#     # Show the plot
#     plt.gca().set_aspect('equal', adjustable='box')
#     plt.show()
#
#


#----------------------------------------- Plot polygon with color fill
def plot_polygons_with_color_fill(polygons,robot_positions):
    """
    Plots multiple polygons with fixed color fills from a given list and adds a legend.

    Args:
    polygons (list of list of tuples): A list where each element is a list of tuples representing vertices of a polygon.
                                       Example: [[(x1, y1), (x2, y2), ...], [(x1, y1), (x2, y2), ...], ...]
    colors (list of str): A list of colors to fill the polygons.
    """
    #plt.figure(figsize=(10,6))
    colors = ['red', 'green', 'blue', 'yellow', 'purple','black']
    fig, ax = plt.subplots(figsize=(8,6))

    # Plot each polygon with a color from the colors list
    for idx, polygon in enumerate(polygons):
        polygon = np.array(polygon)
        color = colors[idx % len(colors)]  # Cycle through colors if more polygons than colors
        ax.fill(polygon[:, 0], polygon[:, 1], color=color, edgecolor='black', linewidth=2, alpha=0.4, label=f'Polygon {idx+1}')
    plt.plot(robot_positions[:, 0], robot_positions[:, 1], 'rx', markersize=15, markeredgewidth=2)

    # Add grid
    #ax.grid(True)

    # Set equal scaling for both axes
    ax.set_aspect('equal')

    # Add legend
    ax.legend(loc='best',bbox_to_anchor=(1, 1),title= 'legend')

    # Show the plot
    plt.tight_layout()
    plt.show()
    ####-------------------- Divide a polygon into Grid points
def generate_grid_in_polygon(polygon_coords, cell_size):
    # Create the convex polygon from the given coordinates
    polygon = Polygon(polygon_coords)

    # Get the bounding box of the polygon
    min_x, min_y, max_x, max_y = polygon.bounds

    # Generate grid points within the bounding box
    grid_points = []
    x = min_x
    while x <= max_x:
        y = min_y
        while y <= max_y:
            point = Point(x, y)
            # Only include points that are inside or on the boundary of the polygon
            if polygon.contains(point) or polygon.touches(point):
                grid_points.append((round(x, 2), round(y, 2)))  # Append the grid point
            y += cell_size
        x += cell_size

    return grid_points


### #--------------------------------- Assign mother grid points to child polygon-------------------------------------

def assign_points_to_polygons(mother_polygon, child_polygons, points):
    # Initialize the list of points for each child polygon
    child_points = [[] for _ in range(len(child_polygons))]

    # Iterate over the points
    for point in points[:]:
        # Check if the point is within the mother polygon (with a small buffer)
        if mother_polygon.buffer(0.001).contains(Point(point)):
            # Iterate over the child polygons
            for i, child_polygon in enumerate(child_polygons):

                # Check if the point is within the child polygon (with a small buffer)
                if child_polygon.buffer(0.01).contains(Point(point)):
                    # Add the point to the child polygon's list of points
                    child_points[i].append(point)
                    # Remove the point from the list of points
                    points.remove(point)
                    # Break out of the loop as the point has been assigned
                    break

    return child_points

#----------------------------------------Plotting of assigned grid_points with assigned polygon--------------
def plot_polygons_with_grid(data,polygon_coords):


    #Input: Data - > A dictionary
    #Output: polygon coordinate list



    # Plot the polygon
    polygon = Polygon(polygon_coords)
    x, y = polygon.exterior.xy
    plt.fill(x, y,color='lightblue', alpha=0.5, edgecolor='black',label = 'polygon')

    # Plot the grid points
    colors =['red','blue','green','magenta','black','violet','yellow']
    for i in range(len(data)):
        grid_points = data[i+1]['grid_points']
        grid_x, grid_y = zip(*grid_points)  # Unpack the grid points
        plt.scatter(grid_x, grid_y, color=colors[i], label='Grid Points',s=3, zorder=5)


    # Plot the polygon
    #plt.fill(points[:, 0], points[:, 1], )

    # Formatting the plot
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Grid Points Inside Polygon')
    plt.legend(loc='lower right')
   # plt.grid(True)
    plt.show()

#


