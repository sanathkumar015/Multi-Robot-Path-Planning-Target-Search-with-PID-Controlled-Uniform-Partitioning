import time

import pygame as pg
import math
import pygame
import numpy as np
#import ctypes
#ctypes.windll.user32.SetProcessDPIAware()

def distance(p1,p2):
    p1 = np.array(p1)
    p2 = np.array(p2)
    return np.linalg.norm(p1-p2)

class Robot:
    def __init__(self,startpos,width,graphics_class):
        self.gfx = graphics_class
        self.m2p =3779.52 # from metert to pixel
        self.w =width
        #self.screen =screen


        self.x = startpos[0]
        self.y = startpos[1]
        self.heading = 0

        self.vl = 0.01*self.m2p
        self.vr = 0.01*self.m2p

        self.maxspeed = 0.02*self.m2p
        self.minspeed = 0.01*self.m2p

        self.min_obs_dist = 100 #minimum obstacle distane is 100 pixel
        self.count_down = 3 #seconds

    def move_p2p(self,start,end,speed,img,map):

        print("moving p2p")
        x = start[0]
        y = start[1]
        #ratio = (end[1]-start[1]) / (end[0]-start[0])
        angle  = math.atan2(end[1]-start[1],end[0]-start[0])
        dir = 0
        print("angle ",angle)
        if (angle==0.0):
            dir = 'F'
            print("go forward")
        elif (abs(angle - math.pi) < 0.01):
            dir = 'B'
            print("go backward")

        elif (abs(angle- math.pi/2) < 0.01):
            dir = 'P'
            print("go perpendicular")
        elif ((angle > 0) and (angle < math.pi/2)):
            dir = 'RD'
            print("downward - right")

        else:
            dir = 'D'
            print("go diagonal")


        dt = 0.09

        last_time = pg.time.get_ticks()
      #  print(last_time)


        if dir == 'F':
            print("dir forward")
            while ((x<end[0]) or (y<end[1])):
                print("in forward loop")
                #dt = (pg.time.get_ticks()-last_time)/1000
                x = x + speed * math.cos(angle) * dt
                y = y +  speed * math.sin(angle) * dt


               # map.fill((0,0,0))
                rotated = pg.transform.rotozoom(img,math.degrees(angle),1)
               # pg.display.update()
               # self.draw_bounding_grid(self.map,self.bounding_coordinate,self.sensor_range,self.robot_dim)
                map.blit(img,(x,y-6))

                pg.display.flip()

                last_time = pg.time.get_ticks()
                print(x,y)
        elif (dir == 'D'):
            while ((x>end[0]) and (y<end[1])):
                print("in diagonal loop")
                #dt = (pg.time.get_ticks()-last_time)/1000
                x = x + speed * math.cos(angle) * dt
                y = y +  speed * math.sin(angle) * dt
                print("dia x",x,"dia y",y)
               # map.fill((0,0,0))
                rotated = pg.transform.rotozoom(img,math.degrees(angle),1)
               # pg.display.update()
               # self.draw_bounding_grid(self.map,self.bounding_coordinate,self.sensor_range,self.robot_dim)
                map.blit(img,(x,y-6))

                pg.display.flip()

                last_time = pg.time.get_ticks()
        elif (dir == 'RD'):
            while ((x<end[0]) or (y<end[1])):
                print("in downward right loop")
                #dt = (pg.time.get_ticks()-last_time)/1000
                x = x + speed * math.cos(angle) * dt
                y = y +  speed * math.sin(angle) * dt
                print("RD x",x,"RD y",y)
               # map.fill((0,0,0))
                rotated = pg.transform.rotozoom(img,math.degrees(angle),1)
               # pg.display.update()
               # self.draw_bounding_grid(self.map,self.bounding_coordinate,self.sensor_range,self.robot_dim)
                map.blit(img,(x,y-6))

                pg.display.flip()

                last_time = pg.time.get_ticks()



        elif (dir == 'P'):
            while(y<end[1]):
                print("perpendicular loopp")
                x = x + speed * math.cos(angle) * dt
                y = y +  speed * math.sin(angle) * dt
                print("p x",x,"p y",y)

               # map.fill((0,0,0))
                rotated = pg.transform.rotozoom(img,math.degrees(angle),1)
               # pg.display.update()
               # self.draw_bounding_grid(self.map,self.bounding_coordinate,self.sensor_range,self.robot_dim)
                map.blit(img,(x,y-6))

                pg.display.flip()

                last_time = pg.time.get_ticks()


        else:
            print("dir backward")
            while ((x>end[0]) or (y>end[1])):
                print("in backward loop")
                #dt = (pg.time.get_ticks()-last_time)/1000
                x = x + speed * math.cos(angle) * dt
                y = y +  speed * math.sin(angle) * dt
                print("back x",x,"back y",y)



               # map.fill((0,0,0))
                rotated = pg.transform.rotozoom(img,math.degrees(angle),1)
#                pg.display.update()
               # self.draw_bounding_grid(self.map,self.bounding_coordinate,self.sensor_range,self.robot_dim)
                map.blit(img,(x,y-6))

                pg.display.flip()

                last_time = pg.time.get_ticks()
                #print(x,y)
        return 1


    def avoid_obs(self,point_cloud,dt):
        closest_obstacle = None
        dist = np.inf

        if len(point_cloud)  > 1:
            for point in point_cloud:
                if dist > distance([self.x,self.y],point):
                    dist = distance((self.x,self.y),point)
                    closest_obstacle = (point,dist)


            if closest_obstacle[1] < self.min_obs_dist and self.count_down > 0:
                self.count_down -= dt
                self.move_backward()

            else:
                self.count_down = 5
                self.move_forward()

    def move_backward(self,dt):
        self.vr = -self.minspeed
        self.vl = - self.minspeed/2

        self.kinematics(dt)


    def move_forward(self,dt):
        self.vr = self.minspeed
        self.vl = self.minspeed
        self.kinematics(dt)

    def move_left(self,dt):
        self.vr = self.minspeed
        self.vl = 0
        self.kinematics(dt)

    def move_right(self,dt):
        self.vr = 0
        self.vl = self.minspeed
        self.kinematics(dt)


    def kinematics(self,dt):

        self.x += ((self.vr+self.vl)/2) * math.cos(self.heading) * dt
        self.y -= ((self.vr+self.vl)/2) * math.sin(self.heading) * dt
        self.heading += (self.vr - self.vl) / self.w * dt

        if self.heading > 2*math.pi or self.heading<-2*math.pi:
            self.heading= 0

        self.vr = max(min(self.maxspeed,self.vr),self.minspeed)
        self.vl = max(min(self.maxspeed,self.vr),self.minspeed)

    def fill_polygon_with_circles_and_draw(self,map,coordinates, circle_radius, interval):
        # Initialize Pygame
        pygame.init()

        # Set up the display
        width, height = 1900,1400
        screen = pygame.display.set_mode((width, height))
        #pygame.display.set_caption("Filled Tetragon")

        # Set the colors
        fill_color = (255, 0, 0)  # Red
        outline_color = (255, 255, 255)  # White
        circle_color = (255, 255, 255)  # White

        # Clear the screen
        map.fill((0, 0, 0))  # Black

        # Create a surface for rendering
        render_surface = pygame.Surface((width, height))

        # Draw the irregular tetragon on the render surface
        pygame.draw.polygon(render_surface, fill_color, coordinates)
        #pygame.draw.polygon(render_surface, outline_color, coordinates, 2)  # Draw polygon outline

        # Blit the render surface onto the main screen
        map.blit(render_surface, (0, 0))

        # Calculate the bounding rectangle of the tetragon
        min_x = min([coord[0] for coord in coordinates])
       # print(min_x)
        max_x = max([coord[0] for coord in coordinates])
        #print(max_x)

        min_y = min([coord[1] for coord in coordinates])
       # print(min_y)
        max_y = max([coord[1] for coord in coordinates])
        #print(max_y)

        # Create a 2D matrix to store the circle centers
        matrix_width = int((max_x - min_x) / interval)
       # print(matrix_width)
        matrix_height = int((max_y - min_y) / interval)
       # print(matrix_height)

        center_matrix = np.zeros((matrix_height, matrix_width, 2), dtype=int)

        # Fill the space inside the tetragon with circles at the given interval
        #print(np.arange(min_y, max_y+interval, interval))
        for x in np.arange(min_x, max_x, interval): #for x in np.arange(min_x, max_x + interval, interval)
            for y in np.arange(min_y, max_y+interval, interval):
               # print(render_surface.get_size())
               # print(x,y)
                if render_surface.get_at((int(x), int(y))) == fill_color:

                    pygame.draw.circle(map, circle_color, (x, y), circle_radius)

                    try:
                        center_x = int((x - min_x) / interval)
                        center_y = int((y - min_y) / interval)
                        center_matrix[center_y, center_x] = (x, y)

                    except IndexError:
                        center_matrix = np.pad(center_matrix, ((0, 1),(0,1),(0, 0)), mode='constant', constant_values=0)
                        center_x = int((x - min_x) / interval)
                        center_y = int((y - min_y) / interval)
                        center_matrix[center_y, center_x] = (x, y)

    # Update the display
        pygame.display.flip()
        time.sleep(1)
        return center_matrix

    def fill_polygon_with_circles(self,coordinates, circle_radius, interval):
        # Initialize Pygame
        pygame.init()
        #import ctypes
        #ctypes.windll.user32.SetProcessDPIAware()
        # Set up the display
        width, height = 800, 800
        screen = pygame.display.set_mode((width, height))
        #pygame.display.set_caption("Filled Tetragon")

        # Set the colors
        fill_color = (255, 0, 0)  # Red
        outline_color = (255, 255, 255)  # White
        circle_color = (255, 255, 255)  # White

        # Clear the screen
        #screen.fill((0, 0, 0))  # Black

        # Create a surface for rendering
        render_surface = pygame.Surface((width, height))

        # Draw the irregular tetragon on the render surface
        pygame.draw.polygon(render_surface, fill_color, coordinates)
        #pygame.draw.polygon(render_surface, outline_color, coordinates, 2)  # Draw polygon outline

        # Blit the render surface onto the main screen
        screen.blit(render_surface, (0, 0))

        # Calculate the bounding rectangle of the tetragon
        min_x = min([coord[0] for coord in coordinates])
        print(min_x)
        max_x = max([coord[0] for coord in coordinates])
        print(max_x)

        min_y = min([coord[1] for coord in coordinates])
        print(min_y)
        max_y = max([coord[1] for coord in coordinates])
        print(max_y)

        # Create a 2D matrix to store the circle centers
        matrix_width = int((max_x - min_x) / interval)
        print(matrix_width)
        matrix_height = int((max_y - min_y) / interval)
        print(matrix_height)

        center_matrix = np.zeros((matrix_height, matrix_width, 2), dtype=int)

        # Fill the space inside the tetragon with circles at the given interval
        for x in range(min_x, max_x, interval):
            for y in range(min_y, max_y, interval):
                if render_surface.get_at((x, y)) == fill_color:
                    pygame.draw.circle(screen, circle_color, (x, y), circle_radius)

                    try:
                        center_x = int((x - min_x) / interval)
                        center_y = int((y - min_y) / interval)
                        center_matrix[center_y, center_x] = (x, y)

                    except IndexError:
                        center_matrix = np.pad(center_matrix, ((0, 1),(0,1),(0, 0)), mode='constant', constant_values=0)
                        center_x = int((x - min_x) / interval)
                        center_y = int((y - min_y) / interval)
                        center_matrix[center_y, center_x] = (x, y)

    # Update the display
        pygame.display.flip()
        return center_matrix


    def sweep(self,map,coordinates,grid_points,access_point,sense_range,robot_dim): #coordinates should be clockwise point of rect/sqr [[0,0],[1200,0],[1200,600],[0,600]]
        self.map = map
        self.bounding_coordinate = coordinates
        self.sensor_range = sense_range
        self.robot_dim = robot_dim

        #grid_points = self.fill_polygon_with_circles(self.bounding_coordinate,3, sense_range)

         #sweep horizontaly from left to right starting at the initial pos , visit in spiral way
        grid_width = grid_points.shape[0]
        grid_height = grid_points.shape[1]
        total_entry = np.count_nonzero(grid_points)

        print("grid shape",grid_points.shape)
        #print("grid height",grid_height)
        print("total points in grid",grid_points.size)
        c=0   #variable for monitoring how much entries have been visited in the bounding box
        start = coordinates[0]
        print("access point",start)
        #self.draw_bounding_grid(self.map,self.bounding_coordinate,self.sensor_range,self.robot_dim)
        #time.sleep(2)
        self.entry_point_crossed = False
        while (c <= total_entry):
            for i in range(grid_width):
                print("entry passed:",c)
                if (i%2)==0:
                    for j in range(0,grid_height,1):
                        print("even row")
                        print(i,j)

                        c+=1
                        #self.draw_bounding_grid(self.map,self.bounding_coordinate,self.sensor_range,self.robot_dim)
                        #pg.display.flip()
                        #time.sleep(.1)
                        print(self.entry_point_crossed)
                        if (self.entry_point_crossed):
                            #print(grid_points[i,j])
                            if((grid_points[i,j]!=[0,0]).any()):
                                print("grid point not zero_1 except start")
                                print("gp ",grid_points[i,j])
                                self.move_p2p(start,grid_points[i,j],20,self.gfx.robot,map)
                                #self.move_p2p(start,grid_points[i,j],10,)
                                start = grid_points[i,j]
                                print("start point",start)
        #                       pg.draw.circle(map,(255,0,0),grid_points[i,j],5)

                                pg.display.flip()



                        else:
                            if((grid_points[i,j]== start).all()):
                                self.entry_point_crossed = True
                                print("grid point not zero_1 at start point")
                                #self.move_p2p(start,grid_points[i,j],20,self.gfx.robot,map)
                                map.blit(self.gfx.robot,(start))
                                #self.move_p2p(start,grid_points[i,j],10,)
                                start = grid_points[i,j]
                                print("start point",start)
        #                       pg.draw.circle(map,(255,0,0),grid_points[i,j],5)

                                pg.display.flip()
                           #time.sleep(0.1)

                else:
                    for j in range (grid_height-1,-1,-1):
                        print("odd row")
                        print(i,j)
                        c+=1
                        print("gp: ",grid_points[i,j])
                        #time.sleep(0.5)
                        if((grid_points[i,j]!=[0,0]).any()):
                            print("grid point not zero_2")
                            self.move_p2p(start,grid_points[i,j],20,self.gfx.robot,map)
                            #self.move_p2p(start,grid_points[i,j],10,)
                            start = grid_points[i,j]
                            print("start point",start)
        #                       pg.draw.circle(map,(255,0,0),grid_points[i,j],5)

                            pg.display.flip()
#                       time.sleep(0.1)



#        rotated = pg.transform.rotozoom(self.gfx,math.degrees(heading),1)
#        rect = rotated.get_rect(center = (x,y))
#        self.map.blit(rotated,rect)




#                        pg.draw.circle(map,(255,0,0),grid_points[i,j],5)
#                        pg.display.flip()
#                        time.sleep(0.1)


            #time.sleep(0.1)





               # time.sleep(0.1)

        #
        return 1

class Graphics:
    def __init__(self,dimensions,robot_img):
        pg.init()

        self.black = (0,0,0)
        self.white =(255,255,255)
        self.red = (255,0,0,)
        self.green = (0,255,0)


        #..........map.............

        self.robot = pg.image.load(robot_img)
        #self.map_img = pg.image.load(map_img)


        self.height = dimensions[1]
        self.width = dimensions[0]

        pg.display.set_caption("obs avoid")
        #import ctypes
        #ctypes.windll.user32.SetProcessDPIAware()
        self.map = pg.display.set_mode((self.width,self.height))
        pg.Surface.fill(self.map,self.black)
        #self.map.blit(self.map_img,(0,0))

    def draw_robot(self,x,y,heading):
        rotated = pg.transform.rotozoom(self.robot,math.degrees(heading),1)
        rect = rotated.get_rect(center = (x,y))
        self.map.blit(rotated,rect)

    def draw_sensor_data(self,point_cloud):
        print(point_cloud)
        for point in point_cloud:
            pg.draw.circle(self.map,self.red,point,3,0)


    def draw_grid(self,robot_dim,sense_range): #sensing range for robot sensor resolution

        x = np.linspace(0,self.width,int(self.width/(robot_dim+sense_range))+1) #যতটি স্যাম্পল নিব তত + 1 লিখতে হবে
        y = np.linspace(0,self.height,int(self.height/(robot_dim+sense_range))+1)
        grid_points = np.empty((len(x),len(y)), dtype=tuple)
        for i in range(len(x)):
            for j in range(len(y)):
                temp = (x[i],y[j])
                grid_points[i][j]=temp

        grid_points = np.transpose(grid_points)
        #print(grid_points)

        for i in range(grid_points.shape[0]):
            for j in range(grid_points.shape[1]):
                pg.draw.circle(self.map,self.white,grid_points[i][j],5)


class Ultrasonic:

    def __init__(self,sensor_range,map):
        self.sensor_range = sensor_range
        self.map_width,self.map_height = pg.display.get_surface().get_size()
        self.map = map

    def sense_obstacle(self,x,y,heading):
        obstacles = []
        x1,y1 = x,y
        start_angle = heading- self.sensor_range[1]
        finish_angle = heading + self.sensor_range[1]
        for angle in np.linspace(start_angle,finish_angle,10,False):

            x2 = x1 + self.sensor_range[0] * math.cos(angle)
            y2 = y1 - self.sensor_range[0] * math.sin(angle)

            for i in range(0,100): #taking samples along the line
                u =i/100
                x = int(x2 * u + x1 * (1-u))
                y = int(y2 * u + y1 * (1-u))
                if 0 < x < self.map_width and 0 < y < self.map_height:
                    color =self.map.get_at((x,y))
                    #print(color)
                    self.map.set_at((x,y),(0,208,255))
                    if (color[0],color[1],color[2]) == (0,0,0):
                        obstacles.append([x,y])
                        break

        return obstacles








