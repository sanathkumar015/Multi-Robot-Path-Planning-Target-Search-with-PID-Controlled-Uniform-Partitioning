from robot_motion_communication_utils import *
from utils import*
from utils2 import*
import pygame
import pygame as pg
from tsp import*
import threading
import sim
polygon_coordinate = [[0, 0], [50.0000000000000, 50.0000000000000], [50, 50], [25.0000000000000, 50.0000000000000]]
AP = polygon_coordinate[0]
scaler = 25.0
bbox  = [[(scaler * num)  for num in sublist] for sublist in polygon_coordinate]
bbox
#grid_point generation
pg.display.init()
#create_empty_dictionary_file("victim_list.txt")

#ctypes.windll.user32.SetProcessDPIAware()
map_dim = (800,800)
gfx = Graphics(map_dim,'bot.png')
start_pos = AP
width = 80
robot= Robot(start_pos, width,gfx)

running = True


grid_points = robot.fill_polygon_with_circles_and_draw(gfx.map,bbox,3,50)
grid_points = grid_points / scaler
grid_points = subtract_value_except(grid_points,25.0,[(0,0)])
print(grid_points)
print(grid_points.shape)
save_in_excel(grid_points,"m3.xlsx")

a = search_tuple(grid_points,(15,5))
print("tuple found at ",a)
pygame.quit()


prox = ['LPS2','LCPS2', 'CPS2', 'RCPS2','RPS2']  #LPS1 = left prox. sensor , RCPS1= right-center prox sensor
pio2 = pioneer('PioneerP3DX2', 'rightMotor2', 'leftMotor2', prox, 30000)
pio2.Initialization(False)


a = 0
detected_victim = None
sequence = sweep_matrix(grid_points)

print("1st one" ,sequence[0])
sequence,_ = tsp(sequence[0],sequence)
print(sequence)

detected_victim_list = []
pause_coverage = 0
duplicate = 1
kk = 0
victim_location = {}
waypoint = []
while True:
    detected_victim = pio2.victim_detection_2()
    print("detected victim ",detected_victim)
    counter = 0
    while counter < len(sequence):
        print("counter ",counter)
        detected_victim = pio2.victim_detection_2()
        print("detected victim ",detected_victim)

        if (detected_victim!= None):
            kk = 'v'+detected_victim
            if kk not in detected_victim_list:
                duplicate = 0
            else :
                duplicate = 1

        if ((detected_victim == None) or duplicate == 1 ):
            try:
                print("moving to: ",sequence[counter]," point")
                #status = self.move_p2p(0,i)
                waypoint.append(sequence[counter])
                status = func_timeout(55, pio2.move_p2p, args=(0,sequence[counter]))
                if (status == 1):
                    print("reached at target")
                counter = counter + 1
            except FunctionTimedOut:
                    print ( "timeout. new target selected")
                    counter = counter + 1
                    pass
        else:
            print("v"+detected_victim," is detected")
            if(check_key_in_file('victim_list.txt','v'+detected_victim)):
                print("some one has rescued it")
                detected_victim_list.append('v'+detected_victim)
            else:
                detected_victim_list.append('v'+detected_victim)
                pos = pio2.get_victim_pos(detected_victim)
                pos = [pos[0]-0.3,pos[1]-0.3]
                waypoint.append(pos)
                try:
                    status = func_timeout(55, pio2.move_p2p, args=(0,pos))

                except FunctionTimedOut:
                        print ( "timeout. new target selected")
                        victim_location.update({'v'+detected_victim : pos})

                        pass
                victim_location.update({'v'+detected_victim : pos})
                append_to_dictionary_file('victim_list.txt','v'+detected_victim,pos)

    if (counter == len(sequence)):
        print("program end")
        pio2.set_velocity(0,0)
        break

print(waypoint)
print(victim_location)
