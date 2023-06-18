import serial
import binascii
import math
import numpy as np


def circle(deg):
    if deg >= 360:
        deg -= 360
    elif deg < 0:
        deg += 360
    return deg


class MyLidar:


    def __init__(self,serial_port='/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0'):
        self.serial_port = serial_port
        self.ser = serial.Serial(port=serial_port,
                            baudrate=230400,  # according to doc
                            timeout=5.0,
                            bytesize=8,  # according to doc
                            parity='N',  # according to doc
                            stopbits=1)  # according to doc
        print('Lidar: Successfully opened serial port: ' + self.serial_port)
        self.ser.close()


    # perform calculations on data for GetData method
    def calc_data(self,str):
        str = str.replace(' ','')

        # converts hexadecimal string data into correct format
        Speed = int(str[2:4]+str[0:2],16)  # /100
        FSA = float(int(str[6:8]+str[4:6],16))/100
        LSA = float(int(str[-8:-6]+str[-10:-8],16))/100
        TimeStamp = int(str[-4:-2]+str[-6:-4],16)
        CS = int(str[-2:],16)

        # initialize lists
        Confidence_i = list()
        Angle_i = list()
        Distance_i = list()
        count = 0

        if(LSA-FSA > 0):
            angleStep = float(LSA-FSA)/(11)
        else:
            angleStep = float((LSA+360)-FSA)/(11)

        counter = 0
        for i in range(0,6*12,6):
            Distance_i.append(int(str[8+i+2:8+i+4] + str[8+i:8+i+2],16)/1000)
            Confidence_i.append(int(str[8+i+4:8+i+6],16))
            Angle_i.append(circle(angleStep*counter+FSA))
            counter += 1

        # return [FSA,LSA,CS,Speed,TimeStamp,Confidence_i,Angle_i,Distance_i]
        return Angle_i, Distance_i


    # get a packet of 12 data points and other associated info
    def get_data(self):

        tmpString = ""
        angles = list()
        distances = list()
        angle_old = 0

        loopFlag = True
        flag2c = False

        self.ser.open()

        while loopFlag:
            b = self.ser.read()  # read one byte from serial port
            tmpInt = int.from_bytes(b,'big')  # bytes to integer rep

            if (tmpInt == 0x54):  # check for header value (0x54)
                tmpString +=  b.hex()+" "  # convert bytes to hexadecimal
                flag2c = True
                continue  # continues the while loop from the start

            elif(tmpInt == 0x2c and flag2c):  # 0x2c is hexadecimal format
                tmpString += b.hex()  # convert bytes to hexadecimal

                # if not full data packet, reset
                if(not len(tmpString[0:-5].replace(' ','')) == 90 ):
                    tmpString = ""
                    flag2c = False
                    continue

                lidarData = self.calc_data(tmpString[0:-5])
                angles.extend(lidarData[0])
                distances.extend(lidarData[1])
                tmpString = ""

                # check for full 360 coverage
                angle_new = circle(angles[-1] - angles[0])
                if angle_new < angle_old:
                    break
                else:
                    angle_old = angle_new

            else:
                tmpString += b.hex()+" "

            flag2c = False

        self.ser.close()

        return angles, distances


    def get_min(self,angle_min=0,angle_max=360):
        angle_min = float(angle_min)
        angle_max = float(angle_max)

        angles, distances = self.get_data()

        if circle(angle_min) != circle(angle_max):
            angles_norm = [circle(angle-angle_min) for angle in angles]

            angle_max = circle(angle_max - angle_min)
            angle_min = 0

            indexes = []
            i = 0
            for angle in angles_norm:
                if (angle >= angle_min) & (angle <= angle_max):
                    indexes.append(i)
                i += 1

            angles = [angles[i] for i in indexes]
            distances = [distances[i] for i in indexes]

        try:
            distance = min(distances)
            angle = angles[distances.index(distance)]

        except ValueError:
            distance = 0
            angle = 0

        return angle, distance


    def get_dist(self,angle):
        angle_set = float(angle)

        angles, distances = self.get_data()

        diff = [abs(circle(angle+180-angle_set)-180) for angle in angles]

        index = diff.index(min(diff))

        angle = angles[index]
        distance = distances[index]

        return angle, distance

    def __del__(self):
        self.ser.close()
        print('Lidar: Successfully closed serial port: ' + self.serial_port)


