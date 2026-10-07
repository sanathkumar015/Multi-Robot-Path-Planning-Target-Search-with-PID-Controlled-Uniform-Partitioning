import math

def euclidean_distance(p1, p2):
    # Calculate Euclidean distance between two points
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def tsp(start_point, points):
    # Start with the specified starting point
    current_point = start_point
    path = []
    points = [tuple(arr) for arr in points]
    remaining_points = set(points)

    total_cost = 0

    while remaining_points:
        # Compute the distances between the current point and all remaining points
        distances = [(euclidean_distance(current_point, p), p) for p in remaining_points]
        # Select the point with the smallest distance
        next_distance, next_point = min(distances)
        # Add the point to the path and remove it from the set of remaining points
        path.append(next_point)
        remaining_points.remove(next_point)
        # Update the total cost
        total_cost += next_distance
        # Set the current point to the next point
        current_point = next_point

    return path, total_cost
