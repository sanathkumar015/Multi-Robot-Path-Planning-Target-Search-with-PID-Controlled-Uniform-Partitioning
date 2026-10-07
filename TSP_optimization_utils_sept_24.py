import numpy as np
import math

from scipy.spatial.distance import cdist
from shapely.geometry import Point, Polygon
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt

def euclidean_distance(p1, p2):
    # Calculate Euclidean distance between two points
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def bray_curtis_distance(p1, p2):
    """
    Calculate Bray-Curtis distance between two points.
    p1, p2: tuple (x, y)
    """
    # Sum of absolute differences
    numerator = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    # Sum of coordinates
    denominator = abs(p1[0] + p2[0]) + abs(p1[1] + p2[1])

    # Handle the case where denominator could be zero
    if denominator == 0:
        return 0  # When both points are at the origin, no distance

    # Calculate Bray-Curtis distance
    return numerator / denominator



def tsp(start_point, points,metric='n'):

    #               I/p:robot_initial_pos, grid_points,metric = e: euclidean, b: 'bray curtic', n: blend of both
    #               O/p: a list of connected point of optimized path and Total cosr
    #


    # Start with the specified starting point
    current_point = start_point
    path = []
    points = [tuple(arr) for arr in points]
    remaining_points = set(points)

    total_cost = 0

    while remaining_points:
        # Compute the distances between the current point and all remaining points
        if metric == 'e':
            combined_distances = [(euclidean_distance(current_point, p), p) for p in remaining_points]
        elif metric == 'b':
            combined_distances = [(bray_curtis_distance(current_point, p), p) for p in remaining_points]
        else:
            distances1 = [(euclidean_distance(current_point, p), p) for p in remaining_points]
            distances2 = [(bray_curtis_distance(current_point, p), p) for p in remaining_points]
            distances = [(euclidean_distance(current_point, p), p) for p in remaining_points]

            w = 0.5  # Weight for Euclidean distance, adjust as needed

            # Combine both distance lists using the weighted summation
            combined_distances = [
                (w * eu_dist + (1 - w) * bray_dist, p1)
                for (eu_dist, p1), (bray_dist, p2) in zip(distances1, distances2)
                if p1 == p2  # Ensuring points are the same in both lists
            ]

        # Select the point with the smallest distance

        next_distance, next_point = min(combined_distances)
       # print(current_point)
        if tuple(current_point) == (-25.0, 3.98):
            print('next_distance',next_distance)
            print('next_point',next_point)
         #   print(distances)
        # Add the point to the path and remove it from the set of remaining points
        path.append(next_point)
        remaining_points.remove(next_point)
        # Update the total cost
        total_cost += next_distance
        # Set the current point to the next point
        current_point = next_point

        #my_list.insert(0, value_to_insert)
    path.insert(0,tuple(start_point))
    return path, total_cost


#-----------------------------------------------------------------------------

def calculate_total_distance(points):
    """
    Calculate the total distance between a list of points sequentially.

    Args:
    points (list of tuples): A list of tuples where each tuple represents a (x, y) coordinate.

    Returns:
    float: The total distance between the points.
    """
    total_distance = 0.0

    for i in range(len(points) - 1):
        point1 = points[i]
        point2 = points[i + 1]
        distance = math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)
        total_distance += distance

    return total_distance



def draw_optimized_paths(optimized_data_dict, polygon_coordinate,file_name= None):

    # Set figure size larger
    plt.figure(figsize=(10, 10))
    colors = ['red', 'blue', 'green', 'magenta', 'black', 'orange',
          'yellow', 'cyan', 'purple', 'brown', 'pink', 'gray',
          'violet', 'teal', 'maroon', 'navy']

    for i in range(len(optimized_data_dict)):

        # Example list of points
        points = optimized_data_dict[i+1]['grid_points']

        # Unpack the points into X and Y coordinates
        x, y = zip(*points)

      # Plot the points and connect them with lines
        plt.plot(x, y, marker='.', linestyle='-', color=colors[i])
      #Plot the robot positions
        plt.plot(optimized_data_dict[i+1]['robot_position'][0], optimized_data_dict[i+1]['robot_position'][1], 'rx', markersize=15, markeredgewidth=2)

    polygon = Polygon(polygon_coordinate)
    x, y = polygon.exterior.xy
    plt.fill(x, y,color='lightblue', alpha=0.5, edgecolor='black',label = 'polygon')

    # Set labels and title
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('TSP optimized path for each robot')
    # Show the plot
    if file_name is not None:
        plt.savefig(file_name+'.png', dpi=300, bbox_inches='tight')

   # plt.grid(True)
    plt.show()

