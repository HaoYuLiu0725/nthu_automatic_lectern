#!/usr/bin/env python3
# coding: utf-8
import paho.mqtt.client as mqtt
from AMR import AMR
from datetime import datetime
import json
import serial
import sys

class NTHU_AL():
    def __init__(self):
        self.AMR = AMR()
        # setting for mqtt communication
        self.main_client = mqtt.Client()
        self.MQTT_BROKER_URL = "localhost"
        self.MQTT_BROKER_PORT = 1883
        self.message = {}
        self.have_message = False
        # serial communication with arduino
        self.arduino = ""
        #self.arduino_port = "/dev/ttyUSB0"
        self.arduino_port = "/dev/ttyACM0"
        self.arduino_baudrate = 9600
        # variables to store information
        self.amr_connection = "連線失敗"
        self.amr_connected = False
        self.battery_status = {"battery_level": "None", "charging": "None"}
        self.status_location = {"X": "None", "Y": "None", "Orientation": "None"}
        self.status_slam_mode = {"map_name": "None", "slam_mode": "None"}
        self.status_power_mode = {"power_mode": "None"}
        self.status_mtr_brake = {"mtr_brake": "None"}
        self.status_led_setting = {"control": "None", "frontR": "None", "frontG": "None", "frontB": "None",
        "frontBri": "None", "frontMode": "None", "rearMode": "None"}
        self.table_height = 0.0
        self.speaker_height = 0.0
        self.goToCenter_result = {"Result": "None"}
        self.goToStandby_result = {"Result": "None"}
        self.goToSide_result = {"Result": "None"}
        self.setLight_result = {"Result": "None"}
        self.mtrBrake_result = {"Result": "None"}
        self.speakers_num = 8 # change here for more speakers
        self.speaker_index = 0
        self.speakers_datalist = [{"name": "None", "height": 0.0} for _ in range(self.speakers_num)]
        self.file_path = "/home/NTHU-AL/nthu_automatic_lectern/speaker_height.txt"
    
    def read_file(self): # read name-height pair from speaker_height.txt
        try:
            with open(self.file_path, 'r') as fh:
                for index, line in enumerate(fh.readlines()):
                    temp = line.split()
                    self.speakers_datalist[index]["name"] = temp[0]
                    self.speakers_datalist[index]["height"] = float(temp[1])
                print(f"File : '{self.file_path}' loaded successfully !")
                for index, item in enumerate(self.speakers_datalist):
                    print(f'Name: {item["name"]}, Height: {item["height"]}')
                    if item["name"] == "None":
                        self.speaker_index = index
        except (OSError, NameError, TypeError, ValueError, AttributeError) as err:
            sys.stderr.write("[ERROR]: " + str(err))
            sys.stderr.write(f"\n[ERROR]: failed to read file: '{self.file_path}'!\n")
        except:
            sys.stderr.write(f"\n[ERROR]: failed to read file: '{self.file_path}'!\n")
            
    # function for mqtt communication
    def mqtt_on_connect(self, client, userdata, flags, rc):
        client.subscribe("/from_website")

    def mqtt_on_message(self, client, userdata, msg): # trigger when receive message from website.py
        self.have_message = True
        #print(f"[{msg.topic}]: {msg.payload}")
        payload = msg.payload.decode('utf-8')
        self.message = json.loads(payload)
        print("-------msg from website-------")
        print("command :", self.message.get("command"))
        print("para :", self.message.get("para"))
        print("------------------------------")

    def mqtt_publish(self): # publish message (from nthal_main.py to website.py)
        payload = {
            "amr_connection" : self.amr_connection,
            "amr_connected" : self.amr_connected,
            "battery_status" : self.battery_status,
            "status_location" : self.status_location,
            "status_slam_mode" : self.status_slam_mode,
            "status_power_mode" : self.status_power_mode,
            "status_mtr_brake" : self.status_mtr_brake,
            "status_led_setting" : self.status_led_setting,
            "table_height": self.table_height,
            "goToCenter_result" : self.goToCenter_result,
            "goToStandby_result" : self.goToStandby_result,
            "goToSide_result" : self.goToSide_result,
            "setLight_result" : self.setLight_result,
            "mtrBrake_result" : self.mtrBrake_result
        }
        self.main_client.publish("/from_main", json.dumps(payload))
        self.have_message = False
        
    # function for arduino communication (change height)
    def changeHeight(self, height: float):
        self.arduino.write(str.encode(height + "\n"))
        self.have_message = False
        
    # function for AMR communication
    def getBatteryStatus(self):
        if self.amr_connected:
            self.battery_status = self.AMR.getBatteryStatus()
        self.mqtt_publish()

    def getRobotStatus(self, para: str):
        if self.amr_connected:
            if para == "location":
                self.status_location = self.AMR.getRobotStatus("location")
            elif para == "slam_mode":
                self.status_slam_mode = self.AMR.getRobotStatus("slam_mode")
            elif para == "power_mode":
                self.status_power_mode = self.AMR.getRobotStatus("power_mode")
            elif para == "mtr_brake":
                self.status_mtr_brake = self.AMR.getRobotStatus("mtr_brake")
            elif para == "led_setting":
                self.status_led_setting = self.AMR.getRobotStatus("led_setting")
        self.mqtt_publish()
    
    def goToLocation(self, locationName: str):
        if self.amr_connected:
            self.mtrBrake_result = self.AMR.MtrBrake("Off")
            if locationName == "center":
                self.goToCenter_result = self.AMR.goToLocation("center")
            elif locationName == "standby":
                self.goToStandby_result = self.AMR.goToLocation("standby")
            elif locationName == "side":
                self.goToStandby_result = self.AMR.goToLocation("side")
        self.mqtt_publish()
    
    def setLight(self, para: str):
        if self.amr_connected:
            if para == "default":
                self.setLight_result = self.AMR.setLight(frontR=0, frontG=0, frontB=0, frontBri=1, frontMode=255, rearMode=0)
            elif para == "customer":
                self.setLight_result = self.AMR.setLight(frontR=0, frontG=0, frontB=0, frontBri=0, frontMode=255, rearMode=0)
            elif para == "purple":
                self.setLight_result = self.AMR.setLight(frontR=150, frontG=0, frontB=170, frontBri=100, frontMode=1, rearMode=1)
        self.mqtt_publish()

    def awakeRobot(self):
        if self.amr_connected:
            self.AMR.setPowerMode("normal")
            self.status_power_mode = self.AMR.getRobotStatus("power_mode")
        self.mqtt_publish()

    def enableMtrBrake(self):
        if self.amr_connected:
            self.mtrBrake_result = self.AMR.MtrBrake("On")
        self.mqtt_publish()

    # MAIN FUNCTION #
    def main(self):
        # connect to arduino
        self.arduino = serial.Serial(self.arduino_port, self.arduino_baudrate, timeout=1)
        self.arduino.reset_input_buffer()
        
        # connect to mqtt
        self.main_client.on_connect = self.mqtt_on_connect
        self.main_client.on_message = self.mqtt_on_message
        self.main_client.connect(self.MQTT_BROKER_URL, self.MQTT_BROKER_PORT)
        self.main_client.loop_start()

        # connect to AMR
        if self.AMR.connect(3) == 1: # 連線成功
            print(datetime.now(), " AMR Connected !!!")
            self.amr_connection = "已成功連線"
            self.amr_connected = True
        else:
            self.amr_connected = False
            print(datetime.now(), " AMR Connection Failed ...")
        
        self.mqtt_publish() # publish once to check mqtt communication
        
        while True: # main loop
            if self.have_message:
                command = self.message.get("command")
                para = self.message.get("para")
                if command == "getBatteryStatus":
                    self.getBatteryStatus()
                elif command == "getRobotStatus":
                    self.getRobotStatus(para)
                elif command == "changeHeight":
                    self.changeHeight(para)
                elif command == "goToLocation":
                    self.goToLocation(para)
                elif command == "setLight":
                    self.setLight(para)
                elif command == "awakeRobot":
                    self.awakeRobot()
                elif command == "enableMtrBrake":
                    self.enableMtrBrake()

            if self.arduino.in_waiting:
                self.table_height = self.arduino.readline().decode('utf-8').rstrip()
                print(f"Now Height: {self.table_height}")
                self.mqtt_publish()



if __name__ == '__main__':
    robot = NTHU_AL()
    robot.main()
