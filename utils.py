import numpy as np
import math
import time
import openpyxl
from sympy import symbols, Eq, cos, sin, pprint, solve

def divide_angle(b_box,n_robot,entry_point):

    # left_equation,lef_slope,left_intercept = create_stline(b_box[0],b_box[3])
    # right_equation,right_slope,right_intercept = create_stline(b_box[1],b_box[2])
    # top_equation,top_slope,top_intercept = create_stline(b_box[3],b_box[2])
    bottom_equation,_,_ = create_stline(b_box[0],b_box[1])


    bbox_len = math.sqrt((b_box[1][1]-b_box[0][1])**2+ (b_box[1][0] - b_box[0][0])**2)
    print("box length: ",bbox_len)
    bbox_wid = math.sqrt((b_box[2][1]-b_box[1][1])**2+ (b_box[2][0] - b_box[1][0])**2)
    print("box length: ",bbox_wid)

    diagonal_angle = math.atan(bbox_wid/bbox_len)
    print("d_angle: ",(diagonal_angle))

    area =  bbox_len * bbox_wid

    diagonal_line_slope = (b_box[0][1]-b_box[2][1])/(b_box[0][0]-b_box[2][0])
    print("d slope: ",diagonal_line_slope)

    right_most_point = b_box[1]

    polygon_coordinate = []


    angle = []
    print(n_robot)

    if (not(check_list_existence(b_box,entry_point))):
            print("entry point is not center")
            for  i in range(n_robot):
                x = (2*(i+1) * area)/(n_robot*(bbox_len-entry_point[0]))
               # print("x: ",x)
                theta = math.atan2(x,(bbox_len-entry_point[0]))

                if(x > bbox_wid):
                  #  print("trap formula")
                   # print("i ",i)
                   # x= 0.5*(2*area - entry_point[0]*bbox_wid) - ((i+1)*area) /n_robot
                    x = (2*area - ((2*(i+1)* area) / n_robot) - entry_point[0]*bbox_wid)/bbox_wid
                    #print("x ",x)


                    if(x<0):
                      #  print("left side")
                        x = 2*(area - (i+1)*area/n_robot)/entry_point[0]
                      #  print("left x: ",x)
                        theta = math.pi - math.atan(x/entry_point[0])
                        angle.append(theta)
                      #  print((theta))
                        pprint(create_stline_angle(entry_point,theta)[0])
                    else:

                        theta = math.atan2(bbox_wid,x - entry_point[0])
                        angle.append(theta)
                       # print(math.degrees(theta))

                        pprint(create_stline_angle(entry_point,theta)[0])



                else:
                   # print("tri. formula")
                   # print(math.degrees(theta))
                   # print(theta)
                    pprint(create_stline_angle(entry_point,theta)[0])
                    angle.append(theta)

            del(angle[-1])
            angle.append(math.pi)
            return angle


    else:
        for  i in range(n_robot):
            x = (2*(i+1) * area)/(n_robot*(bbox_len-entry_point[0]))
            #print("x: ",x)
            theta = math.atan2(x,(bbox_len-entry_point[0]))
            if(x > bbox_wid):
               # print("trap formula")
               # print("i ",i)
               # x= 0.5*(2*area - entry_point[0]*bbox_wid) - ((i+1)*area) /n_robot
                x = (2*area - ((2*(i+1)* area) / n_robot) - entry_point[0]*bbox_wid)/bbox_wid
               # print("x ",x)
                theta = math.atan2(bbox_wid,x - entry_point[0])
                angle.append(theta)
                pprint(create_stline_angle(entry_point,theta)[0])


            else:
              #  print("tri. formula")
              #  print(math.degrees(theta))
              #  print(theta)
                pprint(create_stline_angle(entry_point,theta)[0])
                angle.append(theta)

        del(angle[-1])
        angle.append(math.pi/2)
        return angle

def divide_area_other_point(b_box,n_robot,entry_point):
    # divide a given rectangular search area, considering a single access point (access point is not a corner point - that's why 'other point' used as name)

    angles = divide_angle(b_box,n_robot,entry_point)

    print(angles)
    rect = b_box
    left_equation,_,_ = create_stline(rect[0],rect[3])
    right_equation,right_slope,right_intercept = create_stline(rect[1],rect[2])
    top_equation,top_slope,top_intercept = create_stline(rect[3],rect[2])
    bottom_equation,_,_ = create_stline(rect[0],rect[1])

    d1_angle = math.atan((b_box[2][1]-b_box[1][1])/(b_box[1][0]-entry_point[0]))
    print("d1 angle ",d1_angle)

    try:
        c = math.atan(b_box[3][1]/entry_point[0])
        print(c)
        d2_angle=  math.pi -c
        print("d2: ",d2_angle)

    except ZeroDivisionError:
        print("entry point is at corner")
        diagonal_line_slope_2  = np.inf
        d2_angle = 89.9999


    #print("d slope: ",diagonal_line_slope)

    right_most_point = b_box[1]

    polygon_coordinates = [] #store all polygon shape coordinate in a single list
    p_index = 0 #polygon interator

    unit_angle = 90/n_robot

    right_middle_flag = True
    left_middle_flag = True

    p_index = []
    has_left_solution = False
    for i in range (len(angles)-1):


        equation,slope,y_intercept = create_stline_angle(entry_point,angles[i])
        if (slope>0):
            angle = math.atan(slope)
        else:
            angle = math.pi + math.atan(slope)
        pprint(equation)
        print("st angle: ",angle)
        if(angle <= d1_angle):
            print("in right side")
            intersection_point = find_intersection_point(equation,right_equation)
            print("ip ",intersection_point)
            polygon_coordinates.append([entry_point,right_most_point,intersection_point])
            print(polygon_coordinates)
            right_most_point = intersection_point
            print("rp ",right_most_point)



        elif ((angle > d1_angle) and (angle < d2_angle)):
            print("in middle side")


            if (right_middle_flag ==True):
                intersection_point = find_intersection_point(equation,top_equation)
                print("ip ",intersection_point)

                polygon_coordinates.append([entry_point,right_most_point,b_box[2],intersection_point])
                right_most_point = intersection_point
                right_middle_flag = False
            else:
                intersection_point = find_intersection_point(equation,top_equation)
                polygon_coordinates.append([entry_point,right_most_point,intersection_point])
                right_most_point = intersection_point
                print("ip ",intersection_point)


        else:
            print("in left side")
            has_left_solution = True

            if (left_middle_flag ==True):
                intersection_point = find_intersection_point(equation,left_equation)
                print("ip ",intersection_point)
                polygon_coordinates.append([entry_point,right_most_point,b_box[3],intersection_point])
                right_most_point = intersection_point
                left_middle_flag = False
            else:
                intersection_point = find_intersection_point(equation,left_equation)
                polygon_coordinates.append([entry_point,right_most_point,intersection_point])
                right_most_point = intersection_point


    check = check_list_existence(b_box,entry_point)
    if(check):

        polygon_coordinates.append([entry_point,right_most_point,b_box[3]])
    else:
        if (has_left_solution):
            polygon_coordinates.append([entry_point,right_most_point,b_box[0]])
        else:
            polygon_coordinates.append([entry_point,right_most_point,b_box[3],b_box[0]])



    return polygon_coordinates

def divide_area_corner(b_box,n_robot,entry_point):
        # divide a given rectangular search area, considering a single access point (access point is a corner point)
    angles = divide_angle(b_box,n_robot,entry_point)
    print(angles)
    rect = b_box
    left_equation,_,_ = create_stline(rect[0],rect[3])
    right_equation,right_slope,right_intercept = create_stline(rect[1],rect[2])
    top_equation,top_slope,top_intercept = create_stline(rect[3],rect[2])
    bottom_equation,_,_ = create_stline(rect[0],rect[1])

    diagonal_line_slope_1 = (entry_point[1]-b_box[2][1]) / (entry_point[0]-b_box[2][0])

    try:
        diagonal_line_slope_2 = (entry_point[1]-b_box[3][1]) / (entry_point[0]-b_box[3][0])


    except ZeroDivisionError:
        print("entry point is at corner")
        diagonal_line_slope_2  = np.inf


    #print("d slope: ",diagonal_line_slope)

    right_most_point = b_box[1]

    polygon_coordinates = [] #store all polygon shape coordinate in a single list
    p_index = 0 #polygon interator

    unit_angle = 90/n_robot

    right_middle_flag = True
    left_middle_flag = True

    p_index = []
    has_left_solution = False
    for i in range (len(angles)-1):

        equation,slope,y_intercept = create_stline_angle(entry_point,angles[i])
        pprint(equation)
        if(slope <= diagonal_line_slope_1):
            print("in right side")
            intersection_point = find_intersection_point(equation,right_equation)
            print("ip ",intersection_point)
            polygon_coordinates.append([entry_point,right_most_point,intersection_point])
            print(polygon_coordinates)
            right_most_point = intersection_point
            print("rp ",right_most_point)



        elif ((slope > diagonal_line_slope_1)):
            print("in middle side")




            if (right_middle_flag ==True):
                intersection_point = find_intersection_point(equation,top_equation)
                print("ip ",intersection_point)

                polygon_coordinates.append([entry_point,right_most_point,b_box[2],intersection_point])
                right_most_point = intersection_point
                right_middle_flag = False
            else:
                intersection_point = find_intersection_point(equation,top_equation)
                polygon_coordinates.append([entry_point,right_most_point,intersection_point])
                right_most_point = intersection_point
                print("ip ",intersection_point)


        else:
            print("in left side")
            has_left_solution = True

            if (left_middle_flag ==True):
                intersection_point = find_intersection_point(equation,left_equation)
                print("ip ",intersection_point)
                polygon_coordinates.append([entry_point,right_most_point,b_box[3],intersection_point])
                right_most_point = intersection_point
                left_middle_flag = False
            else:
                intersection_point = find_intersection_point(equation,left_equation)
                polygon_coordinates.append([entry_point,right_most_point,intersection_point])
                right_most_point = intersection_point


    check = check_list_existence(b_box,entry_point)
    if(check):
        polygon_coordinates.append([entry_point,right_most_point,b_box[3]])
    else:
        if (has_left_solution):
            polygon_coordinates.append([entry_point,right_most_point,b_box[0]])
        else:
            polygon_coordinates.append([entry_point,right_most_point,b_box[3],b_box[0]])



    return polygon_coordinates

def calculate_polygon_area(vertices):
    n = len(vertices)

    area = 0

    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        area += (x1 * y2 - x2 * y1)

    return abs(area) / 2

def check_list_existence(list_of_four_points, target_point):
    # check a point (entry point) is included in the bounding box
    for sublist in list_of_four_points:
        if sublist == target_point:
            return True
    return False

def create_stline(point1, point2):
    #create Straight line equation using two given points
    x, y = symbols('x y')

    x1, y1 = point1
    x2, y2 = point2

    if (x2-x1)==0:
        return Eq(x,x1), np.inf,0
    else:

    # Calculate the slope
        slope = (y2 - y1) / (x2 - x1)

        # Calculate the y-intercept
        y_intercept = y1 - slope * x1

        # Create the equation symbolically
        equation = Eq(y, slope * x + y_intercept)
        #pprint(equation)
        return equation, slope, y_intercept

def create_stline_angle(point, angle_rad):
        #create Straight line equation using a given point and an angle
    x, y = symbols('x y')
    x0, y0 = point

    # Convert the angle from degrees to radians
    #angle_rad = angle_deg * (3.14159 / 180)

    # Calculate the slope
    slope = round(sin(angle_rad) / cos(angle_rad),5)

    # Calculate the y-intercept
    y_intercept = round((y0 - slope * x0),5)

    # Create the equation symbolically
    equation = Eq(y, slope * x + y_intercept)


    return equation,slope,y_intercept

def find_intersection_point(equation1, equation2):
    # Solve the equations to find the intersection point
    solution = solve((equation1, equation2), (symbols('x'), symbols('y')))
    return list(solution.values())

def save_in_excel(matrix,name):
    # Example 2D matrix with tuples
   # matrix = np.empty((5, 5), dtype=tuple)  # Empty matrix for demonstrtion
    row = matrix.shape[0]
    col = matrix.shape[1]

   # Assign tuple values for demonstration

    # Create a new Excel workbook
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    # Iterate over the matrix and write each tuple value to the corresponding cell
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            cell_value = str(matrix[i, j])
            sheet.cell(row=i+1, column=j+1, value=cell_value)

    # Save the workbook to an Excel file
    output_file = name
    workbook.save(output_file)


    import numpy as np

def subtract_value_except(matrix, value, exception_tuples):
    result = np.copy(matrix)  # Create a copy of the matrix to avoid modifying the original

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if tuple(matrix[i, j]) not in exception_tuples:
                result[i, j] = (matrix[i, j][0] - value, matrix[i, j][1] - value)

    return result

def sweep_matrix(matrix):
    sequence = []
    specific_value = np.array([0, 0.])
    num_rows, num_cols, _ = matrix.shape
    direction = 1  # 1 for moving right, -1 for moving left

    for i in range(num_rows):
        if i % 2 == 0:
            for j in range(num_cols):
                if j < num_cols and not np.array_equal(matrix[i, j], specific_value):
                    #print("c1")
                    sequence.append(matrix[i,j])
                elif j >= num_cols:

                    #print(matrix[i + 1, num_cols - 1], end=' ')
                    sequence.append(matrix[i + 1, num_cols - 1])
        else:
            for j in range(num_cols - 1, -1, -1):
                if j >= 0 and not np.array_equal(matrix[i, j], specific_value):
                    #print("c2")
                    sequence.append(matrix[i,j])
                elif j < 0:
                    #print(matrix[i + 1, 0], end=' ')
                    sequence.append(matrix[i + 1, num_cols - 1])
    return sequence

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def largest_edge(vertices):
    max_distance = 0
    initial_point = ()
    final_point = ()

    for i in range(len(vertices)-1):
        x1, y1 = vertices[i]
        x2, y2 = vertices[i+1]
        curr_distance = distance(x1, y1, x2, y2)

        if curr_distance > max_distance:
            max_distance = curr_distance
            initial_point = (x1, y1)
            final_point = (x2, y2)

    # Handle the edge case of the last vertex to the first vertex
    x1, y1 = vertices[-1]
    x2, y2 = vertices[0]
    curr_distance = distance(x1, y1, x2, y2)
    if curr_distance > max_distance:
        initial_point = (x1, y1)
        final_point = (x2, y2)

    return initial_point, final_point


def determine_orientation(bbox,entry_point): #bbox should be given in cartesian coordinate, not pygame coordinate
    initial,final = largest_edge(bbox)
    temp = initial
    if (final==entry_point):
        initial = final
        final = temp

    orientation = math.degrees(math.atan2((final[1]-initial[1]),(final[0] - initial[0])))
    return orientation

def is_point_inside_polygon(point, polygon_vertices):
    x, y = point
    num_vertices = len(polygon_vertices)
    inside = False

    p1x, p1y = polygon_vertices[0]
    for i in range(num_vertices + 1):
        p2x, p2y = polygon_vertices[i % num_vertices]

        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        x_intersect = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= x_intersect:
                            if x_intersect == x:
                                # Point lies on the edge of the polygon
                                return True
                            inside = not inside
        p1x, p1y = p2x, p2y

    return inside

def levy_flight_random_num_generator(num_steps,alpha):

    values = []

    for i in range(num_steps):
        if (i%2==0):
            dt =  np.random.power(alpha,1)
            values.append(dt.tolist())
        else:
            angle = np.random.uniform(-math.pi,math.pi,1)
            values.append(angle.tolist())
    values = [item for sublist in values for item in sublist]
    return values

#for going from one to another point, calculate target orientation wrt x axis + side
def calculate_target_ori(current_point,target_point):
    point_x = target_point[0]
    point_y = target_point[1]
    origin_x = current_point[0]
    origin_y = current_point[1]
    delta_x = point_x - origin_x
    delta_y = point_y - origin_y
    angle_rad = math.atan2(delta_y, delta_x)
    angle_deg = math.degrees(angle_rad)
    if angle_deg < 0:
        angle_deg += 360

    if (angle_deg>180):
        angle_deg = -(angle_deg-360)
    else:
        angle_deg = angle_deg

    return angle_deg

def search_tuple(array, target):
    # Convert the target tuple into a numpy array for element-wise comparison
    target_arr = np.array(target)

    # Iterate over each element in the array
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            # Compare the current element with the target
            if np.array_equal(array[i, j], target_arr):
                # Return the position (i, j) if the target is found
                return (i, j)

    # Return None if the target is not found
    return None

def search_tuple_add_value(array, target, value):
    # Convert the target tuple into a numpy array for element-wise comparison
    target_arr = np.array(target)

    # Iterate over each element in the array
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            # Compare the current element with the target
            if np.array_equal(array[i, j], target_arr):
                # Add the specific value to the found tuple element
                array[i, j] = tuple(elem + value for elem in array[i, j])
                # Return the position (i, j) if the target is found
                #return (i, j)

    # Return None if the target is not found
    return array

# Example usag
def append_to_dictionary_file(filename, key, value):
    try:
        with open(filename, "r") as file:
            content = file.read()
            data = ast.literal_eval(content)
    except FileNotFoundError:
        data = {}

    data[key] = value

    with open(filename, "w") as file:
        file.write(str(data))

def create_empty_dictionary_file(filename):
    empty_dict = {}

    with open(filename, "w") as file:
        file.write(str(empty_dict))
create_empty_dictionary_file("haila.txt")

def check_key_in_file(filename, key):
    with open(filename, "r") as file:
        content = file.read()
        data = eval(content)
        return key in data


def euclidean_distance(p1, p2):
    # Calculate Euclidean distance between two points
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def find_minimum_cost_path(start_point, points):
    # Start with the specified starting point
    points = [tuple(arr) for arr in points]
    current_point = start_point
    path = []
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

def solve_circles(center1,r1,center2,r2,center3,r3):
    import numpy as np

    center = [center1,center2,center3]
    radius = [r1,r2,r3]

    g1 = -center1[0]
    f1= -center1[1]
    c1 = (g1**2+f1**2-r1**2)
    #print(g1,f1,c1)

    g2 = -center2[0]
    f2= -center2[1]
    c2 = (g2**2+f2**2-r2**2)
    #print(g2,f2,c2)

    g3 = -center3[0]
    f3= -center3[1]
    c3 = (g3**2+f3**2-r3**2)
    #print(g3,f3,c3)

    a1 = 2*(g1-g2)
    b1 = 2*(f1-f2)
    k1 = (c1-c2)

    a2 = 2*(g2-g3)
    b2 = 2*(f2-f3)
    k2 = (c2-c3)

    denominator = (a1*b2-a2*b1)


    if ((a1*b2-a2*b1)==0): #if all circle internally touched at same point ,then the denomitar is zero,
                            #we solve this case by taking solution of a circle and st_line
        solution = solve_circle_stline(center1,center2,center1,r1)

    else:
        x = (b1*k2-b2*k1)/ denominator
        y = (k1*a2 - k2*a1)/denominator
        solution = [(x,y)]



    for i in range (len(solution)):#check the solution point goes through all circle or not

        point = solution[i-1]
        value = 0
        for j in range(3):
            value = value + check_point_in_circle(solution[i-1],center[j-1],radius[j-1])

        if(value==3):
            return(list(np.round(point,3)))
        else:
            pass

    return 0 #if no solution then return 0

def check_point_in_circle(point, center, radius): #check the solutions are going through all point to validate a solution
    # Calculate the distance between the point and the center of the circle
    distance = math.sqrt((point[0] - center[0])**2 + (point[1] - center[1])**2)

    # Check if the distance is less than or equal to the radius
    if (distance == radius):
        return 1
    else:
        return 0

def solve_circle_stline(point1,point2,center,radius): #function for solution of circle and st_line
    _,m,c= create_stline(point1,point2)
    g = -center[0]
    f = -center[1]
    k= g**2+f**2-radius**2

    A = (1+m**2)
    B = (2*m*c + 2*g + 2*f*m )
    C = (2*f*c + k) + c**2
    #print(A,B,C)
    solution_x = np.roots([A,B,C])
    solution_y = [m*solution_x[0]+c,m*solution_x[1]+c]
    solution = [(solution_x[0],solution_y[0]),(solution_x[1],solution_y[1])]

    #print(solution)
    return solution


