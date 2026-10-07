How to run overall code for thesis?
---------------------------------------

1.run library files: (optional)

a)robot_motion_communication_utils.py: All functions of robot movement, heading correction, position, communications are written here
b)Multi_Robot_area_allocation_utilities_Sept_24_v2.py: All necessary function for area allocation, grid division, plotting of allocation regions are described here
c)TSP_optimization_utils_sept_24.py: function of TSP optimization of grid points , plotting of optimized grid points 
d)central_dictionary_handling_utils_sept24.py: functions for writing , reading from dictionaries are written here. It contains necessary functions for tracking the detected number of vcitims



2. Run Multi Robot Area Allocation & TSP opt- Main file - Sept 24
	It allocates uniform area and generate grid points, optimize the grid points, store the grid points in 'TSp optimized waypoints.txt' using dictionary function of lib (d)
	
3. Start simulation in coppeliaSim (Conference Paper > Simulation scene [four simulation scenes are there]

4. Run pioneer robot 1.py,...........etc
5. Run victim_sept24.py, which communicates with all robots using multi-threading mechanism


