import sys
import os
import subprocess
from HandController import HandController

#password = 0
one = 0
two = 0
# Define the callbacks
def go_callback(event):
    print("Password: *")
    global one
    one += 1
    print(one)

def stop_callback(event):
    global one,two
    if(one == 1):
        print("Password: **")
        print("Unlocked Successful")
        two += 1
        print(one,two)
        hc.stop()
        print("Human Detection on")
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pedestrian_file = os.path.join(current_dir, "pedestrian.py")
        print("Pedestrian function called")
        subprocess.run(["python", pedestrian_file])
        
    else:
        one = 0

    





# Define the config
config = {
    'pose_actions' : [
        {'name': 'GO', 'pose':'FIVE', 'hand':'any', 'callback': 'go_callback'},
        {'name': 'STOP', 'pose':'TWO', 'hand':'any', 'callback': 'stop_callback'},
    ],
    'renderer': 
    {   
        'enable': False,

        'args':
        {
            'output': None,
        }

    }
}


# Create a HandController instance
hc = HandController(config)


# Start the loop
print("Calling the loop function")
hc.loop()
