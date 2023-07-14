#!/usr/bin/env python3
# coding: utf-8
from AMR import AMR
from datetime import datetime
from flask import Flask, render_template, request

class NTHU_AL():
    def __init__(self):
        self.AMR = AMR()
        self.amr_connection = "連線失敗"
        self.amr_connected = False
        self.location = "location"
        self.battery_level = "battery_level"
        self.charging = "charging"
        self.slam_mode = "slam_mode"
        self.power_mode = "power_mode"
    
    def connect_amr(self):
        if self.AMR.connect(3) == 1: # 連線成功
            print(datetime.now(), " AMR Connected !!!")
            self.amr_connection = "已成功連線"
            self.amr_connected = True
        else:
            print(datetime.now(), " AMR Connection Failed ...")

    def getRobotStatus_location(self):
        if self.amr_connected:
            location = str(self.AMR.getRobotStatus("location"))
        else:
            location = "location"
        print(location)
        return location

    def getRobotStatus_battery_level(self):
        if self.amr_connected:
            battery_level = self.AMR.getRobotStatus("battery_level")
        else:
            battery_level = "battery_level"
        print(battery_level)
        return battery_level

    def getRobotStatus_charging(self):
        if self.amr_connected:
            charging = self.AMR.getRobotStatus("charging")
        else:
            charging = "charging"
        print(charging)
        return charging

    def getRobotStatus_slam_mode(self):
        if self.amr_connected:
            slam_mode = self.AMR.getRobotStatus("slam_mode")
        else:
            slam_mode = "slam_mode"
        print(slam_mode)
        return slam_mode
    
    def getRobotStatus_power_mode(self):
        if self.amr_connected:
            power_mode = self.AMR.getRobotStatus("power_mode")
        else:
            power_mode = "power_mode"
        print(power_mode)
        return power_mode

robot = NTHU_AL()
app = Flask(__name__)
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('getRobotStatus_location') == '取得目前位置及方向':
            robot.location = robot.getRobotStatus_location()
        elif request.form.get('getRobotStatus_battery_level') == '取得目前電量':
            robot.battery_level = robot.getRobotStatus_battery_level()
        elif request.form.get('getRobotStatus_charging') == '是否充電中':
            robot.charging = robot.getRobotStatus_charging()
        elif request.form.get('getRobotStatus_slam_mode') == '取得目前 SLAM 模式':
            robot.slam_mode = robot.getRobotStatus_slam_mode()
        elif request.form.get('getRobotStatus_power_mode') == '取得目前電源管理模式':
            robot.power_mode = robot.getRobotStatus_power_mode()
        else:
            pass # unknown
    
    # h_xxxxx is variable in index.html
    return render_template("index.html",\
        h_amr_connection = robot.amr_connection,\
        h_location = robot.location,\
        h_battery_level = robot.battery_level,
        h_charging = robot.charging,\
        h_slam_mode = robot.slam_mode,\
        h_power_mode = robot.power_mode)

if __name__ == '__main__':
    robot.connect_amr()
    app.debug = True
    app.run('192.168.69.1')
