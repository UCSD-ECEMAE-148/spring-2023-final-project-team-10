import sys
import os
import multiprocessing as mp
sys.path.append('/home/jetson/projects/depthai_hand_tracker')
from HandController import HandController
from pedestrian import cam_process
from mylidar import MyLidar
from pyvesc import VESC
import math
import time

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

        print('Starting main process.')
        main()

    else:
        one = 0

def lidar_process(lidar_q,angle_range_q):
    serial_port_lidar = '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0'
    lidar = MyLidar(serial_port=serial_port_lidar)
    angle_min = 157.5
    angle_max = 202.5
    try:
        while True:
            while not angle_range_q.empty():
                angle_min, angle_max = angle_range_q.get()
            #start = time.time()
            angle, dist = lidar.get_min(angle_min,angle_max)
#            while not lidar_q.empty():
#                lidar_q.get()
            lidar_q.put([angle,dist])
            #end = time.time()
            #print(end-start)
    except KeyboardInterrupt:
        print('Stopped lidar process.')

def main():
    mp.set_start_method('spawn')

    cam_q = mp.Queue()
    cam_p = mp.Process(target = cam_process, args = (cam_q,))
    cam_p.start()
    print('Started camera process.')

    lidar_q = mp.Queue()
    angle_range_q = mp.Queue()
    lidar_p = mp.Process(target = lidar_process, args = (lidar_q,angle_range_q))
    lidar_p.start()
    print('Started lidar process.')

    serial_port_vesc = '/dev/serial/by-id/usb-STMicroelectronics_ChibiOS_RT_Virtual_COM_Port_304-if00'
    motor = VESC(serial_port=serial_port_vesc)
    print("Motor firmware: ", motor.get_firmware_version())
    motor.set_servo(0.45)
    motor.set_rpm(0)

    id_count = {}
    real_id = None
    pos = ()
    detected = False
    stop = False

    a = 0.005
    dist_set = 1.5
    dist_set2 = 1
    K = 5000
    rpm_max = 4000
    rpm_min = 800

    time_step = 0
    angle = 0
    angle_old = 0
    angle_smooth = 0
    rpm_set = 0

    try:
        while True:

            if not cam_q.empty():
                detected = False
                while not cam_q.empty():
                    id_data = (cam_q.get())
                id_list = list(id_data.keys())
                if id_list:
                    print(id_list)
                for ID in id_list:
                    if ID in id_count:
                        id_count[ID] += 1
                    else:
                        id_count[ID] = 1
                    if id_count[ID] > 10 and not real_id:
                        real_id = ID
                    if(ID == real_id):
                        pos = id_data[ID]
                        detected = True
                        angle_min = math.atan((pos[0]-640)/640*math.tan(40*math.pi/180))*180/math.pi + 180
                        angle_max = math.atan((pos[2]-640)/640*math.tan(40*math.pi/180))*180/math.pi + 180
#                        print([pos[0],pos[2]])
#                        print([angle_min,angle_max])
                        angle_range_q.put([angle_min,angle_max])
                if not detected:
                    angle_range_q.put([157.5,202.5])
#                print(id_count)

            start = time.time()

            if not lidar_q.empty():
                angle_old = angle
                while not lidar_q.empty():
                    angle, dist = lidar_q.get()
                if type(angle) == float and type(dist) == float:
                    angle -= 180
                    angle = max([min([angle,27]),-27])
                    if dist > dist_set and detected:
                        rpm_set = rpm_min + min([K*(dist-dist_set),rpm_max-rpm_min])
                    elif (dist < dist_set and detected) or dist < dist_set2:
                        rpm_set = -rpm_min + max([K*(dist-dist_set),-rpm_max+rpm_min])
                    else:
                        angle = angle_old
                        rpm_set = 0
                else:
                    angle = angle_old
                    rpm_set = 0
                #rpm_smooth = (1-alpha)*rpm_smooth + (alpha)*rpm_set
                motor.set_rpm(int(rpm_set))

            alpha = a*time_step/0.001
            angle_smooth = (1-alpha)*angle_smooth + (alpha)*angle
            servo = (angle_smooth + 32)/72
            motor.set_servo(servo)

            #print('Time step: %.5f, Lidar output: %.2f, Servo setpoint: %.2f, Distance: %.2f, RPM setpoint: %d' % (time_step,angle,angle_smooth,dist,rpm_set) )

            end = time.time()
            time_step = end-start

    except KeyboardInterrupt:
        print('Stopped main process.')
        motor.set_servo(0.45)
        motor.set_rpm(0)
        motor.stop_heartbeat()
        print('Stopped VESC.')



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



if __name__ == '__main__':
    # Create a HandController instance
    hc = HandController(config)

    # Start the loop
    print("Calling the loop function")
    hc.loop()
