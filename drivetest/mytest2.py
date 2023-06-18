from pyvesc import VESC
import time


serial_port = '/dev/serial/by-id/usb-STMicroelectronics_ChibiOS_RT_Virtual_COM_Port_304-if00'


# test the throttle and the steering
def test_servo():
    try:
        motor = VESC(serial_port=serial_port)
        print("Firmware: ", motor.get_firmware_version())

        motor.set_servo(0.45)
        motor.set_rpm(0)

        while True:
            try:
                servo = input('Input a number between 0 and 1: ')
                servo = float(servo)
                print(f'Setting servo to {servo}.')
                motor.set_servo(servo)
            except ValueError:
                break
    except KeyboardInterrupt:
        pass

    motor.stop_heartbeat()
    print('VESC: Successfully stopped.')


def test_rpm():
    motor = VESC(serial_port=serial_port)
    print("Firmware: ", motor.get_firmware_version())

    motor.set_servo(0.45)
    motor.set_rpm(0)
    try:
        while True:
            rpm = input('Input a value for rpm: ')
            try:
                rpm = int(rpm)
                print(f'Setting rpm to {rpm}')
                motor.set_rpm(rpm)
    #            time.sleep(1)
    #            for i in range(10):
    #                try:
    #                    duty = motor.get_duty_cycle()
    #                    print(f'Duty Cycle is {duty}')
    #                except AttributeError:
    #                    print('Attribute Error!?')
    #                    continue
            except ValueError:
                break
    except KeyboardInterrupt:
        pass
    
    motor.stop_heartbeat()
    print('VESC: Successfully stopped.')


if __name__ == '__main__':
    test_rpm()
