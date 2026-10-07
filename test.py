
#################################################################___________BOX plot of partitioning accuracy_________________####################################
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np
#import numpy as np

# Example % error data for each setup
setup_1 = [0.132, 0.0, 0.001, 0.01, 0.132]
setup_2 = [0.095, 0.028, 0.171, 0.189, 0.049]
setup_3 = [0.115, 0.023, 0.005, 0.209, 0.076]
setup_4 = [0.221, 0.269, 0.273, 0.074, 0.008, 0.144]

#Combine data into a list of lists
data = [setup_1, setup_2, setup_3, setup_4]

# Colors for different setups
colors = ['lightblue', 'lightgreen', 'lightpink', 'lightsalmon']

# Create the figure
plt.figure(figsize=(8, 6))

# Box plot with custom colors and median/mean line styles
box = plt.boxplot(
    data,
    labels=['Setup 1', 'Setup 2', 'Setup 3', 'Setup 4'],
    patch_artist=True,  # Enables fill colors
    meanline=True,  # Show the mean line
    showmeans=True  # Ensures the mean line is displayed
)

# Apply fill colors for each box
for patch, color in zip(box['boxes'], colors):
    patch.set_facecolor(color)

# Set median line to dashed style
for median in box['medians']:
    median.set_linestyle('--')
    median.set_color('red')

# Set mean line to solid style
for mean in box['means']:
    mean.set_linestyle('-')
    mean.set_color('blue')
    mean.set_linewidth(1.5)

# Create custom legend handles
legend_elements = [
    mpatches.Patch(color='lightblue', label='Setup 1'),
    mpatches.Patch(color='lightgreen', label='Setup 2'),
    mpatches.Patch(color='lightpink', label='Setup 3'),
    mpatches.Patch(color='lightsalmon', label='Setup 4'),
    mlines.Line2D([], [], color='blue', linestyle='-', label='Mean'),
    mlines.Line2D([], [], color='red', linestyle='--', label='Median')
]

# Add legend to the plot
plt.legend(handles=legend_elements, loc='upper left', fontsize=10,)

# Add titles and labels
plt.title("Error Analysis Across Simulation Setups", fontsize=14)
plt.ylabel("Partitioning Error(%)", fontsize=12)
plt.xlabel("Simulation Setup", fontsize=12)

# Show the plot
plt.grid(axis='y', linestyle=':', linewidth=0.7)
plt.tight_layout()
plt.savefig("Box plot of %%error across different simulation setup.png", dpi=300, bbox_inches='tight', pad_inches=0.1)
plt.show()
