from pyvesc import VESC
import time

serial_port = '/dev/serial/by-id/usb-STMicroelectronics_ChibiOS_RT_Virtual_COM_Port_304-if00'

# test the throttle and the steering
def test():
    motor = VESC(serial_port=serial_port)
    print("Firmware: ", motor.get_firmware_version())

    motor.set_servo(0.45)

    # run motor and print out rpm for ~2 seconds
    motor.set_duty_cycle(.1)
    for i in range(20):
        time.sleep(0.1)
        try:
            print(motor.get_measurements().rpm)
        except AttributeError:
            print('Attribute Error!?')
            continue
    motor.set_rpm(0)

    # sweep servo through full range
    motor.set_servo(0)
    time.sleep(1)
    motor.set_servo(1)
    time.sleep(1)
    motor.set_servo(0.5)

    # time the measurements
    #start = time.time()
    #motor.get_measurements()
    #stop = time.time()
    #print("Getting values takes ", stop-start, "seconds.")

    # IMPORTANT: YOU MUST STOP THE HEARTBEAT IF IT IS RUNNING
    # BEFORE IT GOES OUT OF SCOPE.
    motor.stop_heartbeat()

if __name__ == '__main__':
    test()
