# SP23 MAE/ECE 148 Team 10 Final Report: 

<p align="center"><img src="img/logo.png" alt="Demo" /></p>

Authors: <br _>
Daniel Na <br _>
David Lim <br _>
Samuel Kweon <br _>

### Project outline:
_A follower robot which identifies a single individual to follow using gesture based password._

### Foundations:
**The project was divided into 3 main parts: gesture recognition, human identification, and Lidar based control:**
1. Gesture recognition was implemented using the DepthAI demo's implementation of the sign language recognition algorithm.
2. Human identification was implemented using the DepthAI demo's implementation of the pedestrian reidentification algorithm.
3. Lidar data was collected using Python and then utilizing the data in order to generate control outputs using PyVesc.

### System summary:
Our code first runs gesture recognition when the program is launched. It will keep searching for a known gesture to be displayed and once the correct gestures are displayed in the correct sequence, the program will terminate the gesture recognition algorithm and launch the human identification algorithm. The human identification algorithm provides outputs for ID an their corresponding coordinates of the bounding box using the top right and bottom left corners by pixels. We isolate the single individual to track by selecting the first human ID to be recognized 8 times. Once this has occurred, the bounding box width and direction to point is calculated using the corner coordinates. The data is then sent to the Lidar by converting the pixel based data into a range of angles to collect the data from. Note that while the Lidar will keep collecting data 360 degrees, we are simply isolating the data at a certain angle range. Once the range and direction has been set, the robot utilizes PyVesc functions in order to achieve a set distance with the nearest object in the scanning angle range. In our case, this was set to 1 meter. 
**PyVesc implementation and PID:**


### Issues/Bugs:
1. We recognized an error in which the Lidar would provide noisy and inaccurate data if there was no object detected within 10 meters in any direction. This meant that large open areas will especially cause issues. It will create false points closer than the human, causing the robot to back up or freeze in place. We believe the only true remedy for this is to utilize a longer range lidar. Another potential resolution worth looking into is a filter to remove any points that jump significantly.
2. Another issue with our implementation was the lack of simultaneous execution of gesture recognition and human identification. While in theory it should be possible, the main cause for concern is the fact that each of the two algorithms attempt to create separate pipelines of data. A potential solution would be to create a single pipeline in a separate code such as the launch code, and the give the launch functions of both algorithms permission to access the single pipeline created rather than each creating their own. We did not have the experience nor time to fully explore this option. 
3. A potential source of inaccuracy we realized upon completion of the project was the difference in angles between the camera and the Lidar due to positional offset. Since the two input sources are not mounted at the same point, the angles that are seen by the camera cannot directly be translated to the Lidar. 

### Potentials for improvement:
There are a couple things our projects could be improved in. 
1. Firstly, it would be significantly improved by resolving the simultaneous gesture detection and human identification since it would open up possibilities for things like pausing and transferring tracking targets. 
2. Secondly, a potential topic of improvement is implementing a protocol to find the target again after the human being tracked has left the camera's field of view. Currently the robot remains stationary if nobody is detected, but if someone was previously detected, it would be useful to have the robot continue turning in the directing the target left the frame until the target is found again. 

Thank you to Jack Silberman, Kishore Nukala, Moises Lopez, and DepthAI for the assistance in producing this project.

### Credits
[Hand Tracker by geaxgx](https://github.com/geaxgx/depthai_hand_tracker.git) <br _>
[Pedestrian Reidentification by luxonis](https://github.com/luxonis/depthai-experiments/tree/master/gen2-pedestrian-reidentification) <br _>
[PyVESC by LiamBindle](https://github.com/LiamBindle/PyVESC.git) <br _>
