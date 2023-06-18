import math
import time
import matplotlib.pyplot as plt
from mylidar import MyLidar

# set up lidar class object
lidar = MyLidar()

# set up the figure
fig = plt.figure(figsize=(8,8))
ax = fig.add_subplot(111, projection='polar')
ax.set_title('Lidar Map (Press E to exit)',fontsize=18)

# exit key
plt.connect('key_press_event', lambda event: exit(1) if event.key == 'e' else None)

while True:
    # get data
    angles, distances = lidar.get_data()

    # convert to radians
    angles = [-math.radians(theta) for theta in angles]

    # get lidar data, plot lidar data
    if('points' in locals()):  # removes previous plot
        points.remove()
    points= ax.scatter(angles, distances, c="red", s=5)
    ax.set_theta_offset(math.pi / 2)  # rotates the plot
    plt.pause(0.01)
    #time.sleep(0.5)
