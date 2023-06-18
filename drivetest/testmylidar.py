from pyvesc import VESC
from mylidar import MyLidar
import time
from multiprocessing import Process, Queue

serial_port = '/dev/serial/by-id/usb-STMicroelectronics_ChibiOS_RT_Virtual_COM_Port_304-if00'

motor = VESC(serial_port=serial_port)
print("Firmware: ", motor.get_firmware_version())
motor.set_servo(0.45)
motor.set_rpm(0)

lidar = MyLidar()

angle_range = 90
angle_forward = 180

angle_min = angle_forward-angle_range/2
angle_max = angle_forward+angle_range/2

def lidar_process(angle_q,dist_q):
    while True:
        #start = time.time()
        angle, dist = lidar.get_min(angle_min,angle_max)
        angle -= angle_forward
        angle = max([min([angle,27]),-27])

        angle_q.put(angle)
        dist_q.put(dist)
        #end = time.time()
        #print(end-start)

time_step = 0
angle = 0
dist = 0
angle_smooth = 0
rpm_smooth = 0
update = True

a = 0.005
dist_set = 1
K = 5000
rpm_max = 4000
rpm_min = 800

if __name__ == '__main__':
    angle_q = Queue()
    dist_q = Queue()
    p = Process(target = lidar_process, args = (angle_q,dist_q))
    p.start()

    try:
        while True:
            start = time.time()

            while not angle_q.empty():
                angle = angle_q.get()

            alpha = a*time_step/0.001
            angle_smooth = (1-alpha)*angle_smooth + (alpha)*angle

            servo = (angle_smooth + 32)/72
            motor.set_servo(servo)

            if not dist_q.empty():
                while not dist_q.empty():
                    dist = dist_q.get()
                if dist > dist_set:
                    rpm_set = rpm_min + min([K*(dist-dist_set),rpm_max-rpm_min])
                else:
                    rpm_set = -rpm_min + max([K*(dist-dist_set),-rpm_max+rpm_min])
                #rpm_smooth = (1-alpha)*rpm_smooth + (alpha)*rpm_set
                motor.set_rpm(int(rpm_set))

            print('Time step: %.5f, Lidar output: %.2f, Servo setpoint: %.2f, Distance: %.2f, RPM setpoint: %d' % (time_step,angle,angle_smooth,dist,rpm_smooth) )

            #time.sleep(0.001)

            end = time.time()
            time_step = end-start

    except KeyboardInterrupt:
        motor.set_servo(0.45)
        motor.set_rpm(0)
        motor.stop_heartbeat()
        print('VESC: Successfully stopped.')

