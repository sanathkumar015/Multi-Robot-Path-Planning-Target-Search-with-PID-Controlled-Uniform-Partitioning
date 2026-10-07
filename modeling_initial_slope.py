import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


# Example data (replace these with your actual data)

# Example data (replace these with your actual data)

target_area = 348  # Target area (constant for all slopes)

# Example Data for setup 4
y_data =  np.array([0,0.1,1,10,18,19,20,21,22,30,45,50,70]) #np.array([0,0.1,1,10,15,16,16.5,20])
areas =  np.array([700,697,678,496,365.15,350,335,320,306.5,202,97,78,30.7])  # Corresponding calculated areas
x_data =  areas - target_area  #np.array([ 352.,349.,330. ,148. ,-13.  ,-146. , -251. , -270. , -317.3]) #np.array([375,372.82,353,154,40.1,16.567,4.732,-79]

#plt.plot(y_data,x_data)
#plt.show()
print(y_data)
def quadratic_func(x, a, b, c ,d ):
    return a*x**3 + b*x**2 + c*x +d

popt, pcov = curve_fit(quadratic_func, x_data, y_data)

# Print the fitted parameters
print(popt)

# Plot the data and the fitted curve
plt.scatter(x_data, y_data, label='Data')
plt.plot(x_data, quadratic_func(x_data, *popt), 'r-', label='Fit')
plt.legend()
plt.show()

