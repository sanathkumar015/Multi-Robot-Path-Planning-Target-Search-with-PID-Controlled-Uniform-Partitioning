import sim
import simConst
import time
import numpy as np
import random
import math
import heapq
#from utils import *
from shapely.geometry import Point, Polygon
from func_timeout import func_timeout, FunctionTimedOut
import time
import threading
import matplotlib.pyplot as plt

print('Program started')
sim.simxFinish(-1)  # just in case, close all opened connections


class pioneer:

    def __init__(self, namepio, nameRightMotor, nameLeftMotor, nameProxSen, port):

        self.x_data = []
        self.y1_data = []
        self.y2_data = []

        # Create a figure and axis
        self.fig, self.ax = plt.subplots()

        # Set up the plots
        self.line1, = self.ax.plot(self.x_data, self.y1_data, label='Variable 1')
        self.line2, = self.ax.plot(self.x_data, self.y2_data, label='Variable 2')

        self.namepio = namepio  # Name of the pio assigned as a class
        self.clientID = -1

        self.nameProxSen =  nameProxSen
        self.clientID = sim.simxStart('127.0.0.1', port, True, True, 5000, 5)
        self.victim = []
        self.detected_victim = []
        self.pause_coverage_flag = 0
        self.last_visited_point = 0

        # #initizalization of victim
        # for i in range(15):
        #     self.victim.append(sim.simxGetObjectHandle(self.clientID,'/'+'V'+str(i+1), sim.simx_opmode_blocking)[1])
        # #print(self.victim)

        if self.clientID == -1:
            print("Connected Failed")
        else:
            print("Connected Successfully")

        self.nameRightMotor = nameRightMotor
        self.nameLeftMotor = nameLeftMotor

        # self.MsgSensor = nameMsgSensor
        # self.LightSensor = nameLightSensor

        self.ProximitySensorNo = len(nameProxSen)
        self.ProximitySensorName = [''] * self.ProximitySensorNo
        self.ProximitySensorHandle = [-1] * self.ProximitySensorNo

        self.MsgSensorHandle = -1
        self.LeftMotorHandle = -1
        self.RightMotorHandle = -1

        err, self.robotHandle = sim.simxGetObjectHandle(self.clientID, '/' + self.namepio, sim.simx_opmode_blocking)
        if err != 0:
            print("Error_pio")

        i = 0
        for name in nameProxSen:
            self.ProximitySensorName[i] = name
            err, self.ProximitySensorHandle[i] = sim.simxGetObjectHandle(self.clientID, '/' + name,
                                                                         simConst.simx_opmode_blocking)
            if err != 0:
                print("Error_" + name)
            i = i + 1
            # print(i)

        err, self.LeftMotorHandle = sim.simxGetObjectHandle(self.clientID, '/' + nameLeftMotor,
                                                       sim.simx_opmode_blocking)
        if err != 0:
            print("Error_LeftMotor")

        err, self.RightMotorHandle = sim.simxGetObjectHandle(self.clientID, '/' + nameRightMotor,
                                                             sim.simx_opmode_blocking)
        if err != 0:
            print("Error_RightMotor")

        # Constants
        self.__HalfDiameter =  0.485/2  # pio radius
        self.__RatioMotor = 10 / 255  # Coppelia code
        self.__MaxVelocity = 255  # Indicates the max speed that motors can reach
        self.__AnchorsNumber = 3  # Number of anchors
        self.__AnchorsName = {'pio0': [0, 0], 'pio2': [0, 0.14], 'pio4': [0.14, 0]}


        # and distance traveled by the message
        self.UnknownNodeList = {}  # stores the nodes with unknown location
        self.Anchor = False  # if itself an anchor or not
        self.AnchorAux = False  # used in MCMM algorithm

        # Communication with other pios
        self.EnableReceived = 1  # to indicate whether it receives messages (0 = no), by default it is listening.
        self.State = False  # to know if it is ready for next action (True = ready)
        self.Memory = []  # memory of the received message
        self.MemoryCount = 0  # memory counter
        self.NeighboursList = {}  # list storing the nearby pios
        self.SwarmState = {}  # store the status of the pios to know if they are ready

        # Parameters for movement
        self.LeftMotorVelocity = 0  # indicates the speed of the pio
        self.RightMotorVelocity = 0
        self.Velocity = 0
        self.time = 0
        self.VO_state = 'Left'
    # ------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------Functions for pios----------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def Initialization(self, flagnoise):
        self.set_velocity(0, 0)
        # if flagnoise:
        #     self.LeftNoise = random.randrange(-30, 30, 1)
        #     self.RightNoise = random.randrange(-30, 30, 1)
        # else:
        #     self.LeftNoise = 0
        #     self.RightNoise = 0

        # Communication with others pios
        self.EnableReceived = 1
        self.State = False
        self.Memory = []
        self.MemoryCount = 0
        self.NeighboursList = {}

        # Parameters for movement
        self.RightMotorVelocity = 0
        self.LeftMotorVelocity = 0
        self.Velocity = 0

    def set_velocity(self, Lmotor, Rmotor):

        self.LeftMotorVelocity = Lmotor
        LeftMotorHandle = self.LeftMotorHandle
        left_velocity = self.__RatioMotor * self.LeftMotorVelocity

        self.RightMotorVelocity = Rmotor
        RightMotorHandle = self.RightMotorHandle
        right_velocity = self.__RatioMotor * self.RightMotorVelocity

        sim.simxSetJointTargetVelocity(self.clientID, LeftMotorHandle, left_velocity, sim.simx_opmode_oneshot)
        sim.simxSetJointTargetVelocity(self.clientID, RightMotorHandle, right_velocity, sim.simx_opmode_oneshot)

    def straight(self, velocity):  # move straight with variable speed, can be used to stop
        self.Velocity = velocity  # at max speed, speed is almost 1 cm/s
        self.set_velocity(velocity, velocity)  # moves in -x direction of pio's coordinate axis
        return True

    def proximity_sensor(self):
        # return detection state (string), obstacle distance (array)
        # max detection range in simulation is set as 1m.

        d_state = ''  # d_state = detection state e.g. '10101'
        obstacle_distance = [] # list for storing the value of distances
        reading = [-1] * self.ProximitySensorNo
        i = 0

        # Reading sensor Data and calculate distance from each prox sensor
        for handle in self.ProximitySensorHandle:
            reading[i] = sim.simxReadProximitySensor(self.clientID, handle, sim.simx_opmode_streaming)
           # print(reading[i])

        # Get distance of obstacle from all five sensor
            if reading[i][1] == 1:
                distance = np.round((reading[i][2][0]**2 + reading[i][2][2]**2)**0.5, 4)
                d_state = d_state+'1'
                obstacle_distance.append(distance)
            else:
                d_state = d_state+'0'
                obstacle_distance.append(np.inf)
            # print('dstate',d_state)
            # print('obs distance',obstacle_distance)

            i = i + 1

        obstacle_distance = np.array(obstacle_distance)
        return d_state, obstacle_distance

    def robot_heading_angle(self):
        # gives the robot heading angle(degree) wrt the +x axis
        # imitate the magnetic sensor

        _, objectHandle = sim.simxGetObjectHandle(self.clientID, "/" + self.namepio,
                                                  sim.simx_opmode_blocking)
        _, angles = sim.simxGetObjectOrientation(self.clientID, objectHandle, sim.sim_handle_parent,
                                                 sim.simx_opmode_blocking)
        angle = angles[2] * 180 / np.pi

       # convert the robot heading as always CCW angle
        #angle = (360 + angle) if (angle < 0) else angle
        return angle

    def find_target_angle(self, obj_name):
        # target direction (angle -degree) w.r.t the origin of coordinate system (+x axis)

            _, objectHandle = sim.simxGetObjectHandle(self.clientID, "/" + obj_name, sim.simx_opmode_blocking)
            _, position = sim.simxGetObjectPosition(self.clientID, objectHandle, sim.sim_handle_parent,
                                                    sim.simx_opmode_blocking)


            # Convert the position data to numpy array
            val = complex(round(position[0], 3), round(position[1], 3))
            angle = np.angle(val) * 180 / np.pi
            # convert the robot heading as always CCW angle
            # if angle < 0:
            #    angle = 360 + angle

            return angle

    def find_target_position(self,target_name):
        err, objectHandle = sim.simxGetObjectHandle(self.clientID, "/" + target_name, sim.simx_opmode_blocking)
        if err != 0:
            print("Error_target")
        _, position = sim.simxGetObjectPosition(self.clientID, objectHandle, -1, sim.simx_opmode_blocking)
        print('')
        val = [round(position[0], 3), round(position[1], 3)]
        return val

    def get_current_simulation_time(self):

        signal_value, signal_string = sim.simxGetStringSignal(self.clientID, "mySimulationTime",
                                                              sim.simx_opmode_streaming)
        signal_value, signal_string = sim.simxGetStringSignal(self.clientID, "mySimulationTime", sim.simx_opmode_buffer)

        if signal_value == sim.simx_return_ok:
            return float(signal_string)
        else:
            return None

    def target_orientation(self, objname): #get target heading  (self frame orientation not wrt to robot) (unnecessary func)
        _, objectHandle = sim.simxGetObjectHandle(self.clientID, "/" + objname, sim.simx_opmode_blocking)
        _, angles = sim.simxGetObjectOrientation(self.clientID, objectHandle, sim.sim_handle_parent,
                                                 sim.simx_opmode_blocking)
        return angles[2] * 180 / np.pi + 180

    def robot_position(self):
        #Get robot position in XY coordinate system. Return [x,y]

        _, robot_position = sim.simxGetObjectPosition(self.clientID, self.robotHandle, -1, sim.simx_opmode_blocking)
        robot_position = [round(num,2) for num in robot_position]
        return robot_position[0:2]

    def adjust_heading(self, target):
        ## Adjust robot heading to the target point.

        print("-------- Adjust Heading Loop-----------")
        tolerance = 10

        #check whether target_coordinate is given or target name is given
        if type(target) == str:
            err, objhandle = sim.simxGetObjectHandle(self.clientID, "/" + target, sim.simx_opmode_blocking)
            if err != 0:
                print("Error " + target)
            target_pos = self.find_target_position(target)
        else:
            target_pos = target


        rel_angle = self.calc_rel_angle(target_pos)
        print("relative angle: " + str(rel_angle))

        if abs(rel_angle) < tolerance:
            print('Going to ', target)
            print("Toward Target")
            self.straight(200)
            return True

        else:
            print('Going to ',target)
            print("Not in same as target dir.")



            if (rel_angle > 180) or (rel_angle <-180):
                if rel_angle > 180:
                    rel_angle = 360-rel_angle
                    print('left turn')
                    speed = math.exp(0.01*abs(rel_angle)+3)
                    print("speed",(0,speed))
                    self.set_velocity(0, speed)
                else:
                    rel_angle = 360+rel_angle
                    print('right turn')
                    speed = math.exp(0.01*abs(rel_angle)+3)
                    print("speed",(speed,0))
                    self.set_velocity(speed, 0)
            elif rel_angle > 0:
                print('right turn')
                speed = math.exp(0.01*abs(rel_angle)+3)
                print("speed",(speed,0))
                self.set_velocity(speed, 0)

            else:
                print('left turn')
                speed = math.exp(0.01*abs(rel_angle)+3)
                print("speed",(0,speed))
                self.set_velocity(0, speed)

    def calc_rel_angle(self,target):

        # calculate the relative angle between robot heading and target point (wrt to robot's coordinate system)
        # input: end point = (x,y) of end point or target point
        # output: rel_angle

        robot_pos = self.robot_position()
        robot_orientation = self.robot_heading_angle()
        print('robot orientation ',robot_orientation) #robot orientation wrt to global coordinate system

        if type(target) == str:
            err,_ = sim.simxGetObjectHandle(self.clientID, "/" + target, sim.simx_opmode_blocking)
            if err != 0:
                print("Error " + target)
            target_pos = self.find_target_position(target)
        else:
            target_pos = target

        # slope is the angle wrt to +X axis, if we consider origin of global coordinate system is shifted to the robot's self coordinate system
        slope = math.atan2((target_pos[1] - robot_pos[1]), (target_pos[0] - robot_pos[0])) * (180/math.pi)
        #slope =  (360+slope) if (slope<0) else slope
        print('slope', slope)
        rel_angle = (robot_orientation - slope)
        return rel_angle

    # def adjust_heading_to_target(self,target,tol = 5):
    #
    #     kp = 1
    #
    #     p_error =0
    #     integral = 0
    #     P,I,D = 0,0,0
    #     while True:
    #         robot_heading  = self.robot_heading_angle()
    #         robot_pos = self.robot_position()
    #         target_pos = self.find_target_position(target)
    #         target_posx = target_pos[0] - robot_pos[0]
    #         target_posy = target_pos[1] - robot_pos[1]
    #
    #
    #         val = complex(round(target_posx, 3), round(target_posx, 3))
    #         angle = np.angle(val) * 180 / np.pi
    #         target_angle = (360 + angle) if (angle < 0) else angle
    #
    #         print("current_robot_heading: ",robot_heading)
    #         print("target_angle",target_angle)
    #         error = target_angle - robot_heading
    #         print("error,", error)
    #         speed = kp * error
    #
    #         if (abs(error) < tol):
    #             break
    #
    #         else:
    #             if (error < 0):
    #                 self.set_velocity(abs(speed),0)
    #                 print("speed: ",speed,0)
    #             else:
    #                 self.set_velocity(0,abs(speed))
    #                 print("speed: ",0,speed)
    #
    #
    #
    #
    #     self.set_velocity(0,0)
    #     return True
    def move_p2p(self,unnecessary_var,target):
    # By calling the robot will rotate its heading towards target and reach the target
            print("-------Move p2p Loop------------")
            tolerance = 0.7
            robot_pos = self.robot_position()

            #check whether target_point is given or target name is given
            if type(target) == str:
                target_pos = self.find_target_position(target)
            else:
                target_pos = target
            while (abs(robot_pos[0] - target_pos[0]) > tolerance or abs( robot_pos[1] - target_pos[1]) > tolerance ):

                print('going to ', target)
                print("not reached")
                heading_flag = self.adjust_heading(target)
                if heading_flag == 1:
                    print("in same dir of target")
                    self.straight(200)

                robot_pos = self.robot_position()
            print("reached at ",target)
            self.straight(0)
            return True,robot_pos

    def send_message(self,message):
         # Send a message to Robot B
        sim.simxSetStringSignal(self.clientID, 'message', message, sim.simx_opmode_oneshot)
        #sim.simxFinish(self.clientID)
        print('sending:', message)
        # Wait for a short period before sending the next message
        time.sleep(0.5)
        return True

    def receive_message(self):

        sim.simxGetStringSignal(self.clientID, 'message', sim.simx_opmode_streaming)
        returnCode, signalValue = sim.simxGetStringSignal(self.clientID, 'message', sim.simx_opmode_blocking)
        if returnCode == sim.simx_return_ok and signalValue:
            try:
                string = signalValue.decode('utf-8')
                if string is None:
                    time.sleep(.5)
                    return 'None'
                else:
                    time.sleep(.5)
                    return string
            except UnicodeDecodeError:
                print("Unicode error")
                print("string")
                pass
        else:
            print("Waiting for message....")

    def set_pos(self,target_position,target_name = None):
        # This function can move any object or robot itself to a target_position instantaneously. Calling for other object doesn't make problem
        # But calling for robot, make the robot to vibrate and behave absurdly .
        if target_name == None:
            target_handle = self.robotHandle
        else:
            _,target_handle = sim.simxGetObjectHandle(self.clientID, "/" + target_name, sim.simx_opmode_blocking)

        sim.simxSetObjectPosition(self.clientID, target_handle, -1, target_position, sim.simx_opmode_oneshot)
        return True

    def  victim_detection_2(self):
        #when message recived by any victim, it send help_1(say)
        #the robot receive the help message extract ID of victim ,here 1
        # if robot can not receive the 'help', the victim send until the nearby robot receive 'help'
        # This process mimic the RFID tag reading event by a robot
        #if received by robot

        message = 'anyone?'+str(self.robotHandle)
        self.send_message(message)
        #time.sleep(.1)
        m = self.receive_message()
        #print(len(m))
        if (m!=message and ( m!='None' and len(m)!=0)):
            print("received msg,",len(m),'by ', self.namepio)
            split_string = m.split('_')
            number = str(split_string[-1])

            victim_handle = self.victim[int(number)-1]

            victim_pos = sim.simxGetObjectPosition(self.clientID,victim_handle,-1,sim.simx_opmode_blocking)[1]
            robot_pos = self.robot_position()
            dist = math.sqrt((robot_pos[0] - victim_pos[0])**2+(robot_pos[1] - victim_pos[1])**2)

            print("received msg,",m,"distance",dist,"split string ",split_string[0])
            if (split_string[0] == 'help' and dist <=3 ):
                print("communication is established with v"+number)
                self.send_message("ok?v"+number+"?"+str(self.robotHandle))
                #queue.put(number)
                return number
            else:
                return None # 100 means 0 here, as 0 may conflict with victim number
        return  None

    def get_victim_pos(self,number):
        number = int(number)
        victim_handle = self.victim[number-1]
        pos = sim.simxGetObjectPosition(self.clientID,victim_handle,-1,sim.simx_opmode_blocking)[1]
        return pos


    import socket

    def send_message_socket(self,sock, message):
        """
        Sends a message through the specified socket.

        Args:
            sock (socket.socket): The socket to send the message through.
            message (str): The message to send.
        """
        try:
            sock.endall(message.encode())
            print(f"Sent message: {message}")
        except Exception as e:
            print(f"Error sending message: {e}")

    def receive_message_socket(self,sock):
        """
        Receives a message from the specified socket.

        Args:
            sock (socket.socket): The socket to receive the message from.

        Returns:
            str: The received message.
        """
        try:
            data = sock.recv(1024).decode()  # Adjust buffer size as needed
            print(f"Received message: {data}")
            return data
        except Exception as e:
            print(f"Error receiving message: {e}")
            return None


    def get_current_simulation_time(self):


       sim_time= sim.simxGetLastCmdTime(self.clientID)
       return sim_time
