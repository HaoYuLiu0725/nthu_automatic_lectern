#!/usr/bin/env python3
# coding: utf-8
from datetime import datetime
from flask import Flask, render_template, request
from flask_mqtt import Mqtt
from nthual_main import NTHU_AL
import json

robot = NTHU_AL()
app = Flask(__name__) # Use Flask to create and handle website
app.config['MQTT_BROKER_URL'] = robot.MQTT_BROKER_URL
app.config['MQTT_BROKER_PORT'] = robot.MQTT_BROKER_PORT
app.config['MQTT_REFRESH_TIME'] = 1.0  
mqtt = Mqtt(app)

# speaker_height to target_height(table_height) function
# target_height = slope * speaker_height + intercept
slope = 0.6763
intercept = -7.6706

def change_height(speaker_height):
    target_height = slope * speaker_height + intercept
    mqtt_publish(command = "changeHeight", para = "{:.2f}".format(target_height))

def store_data(speaker_name, speaker_height, index):
    robot.speakers_datalist[index]["name"] = speaker_name
    robot.speakers_datalist[index]["height"] = speaker_height
    print(f"Data stored: {robot.speakers_datalist}")

def mqtt_publish(**messageDict):
        mqtt.publish("/from_website", json.dumps(messageDict))

# Main function for website, handle button press -------------------------------------------
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('goToLocation_center') == '前往舞台中央(center)':
            mqtt_publish(command = "goToLocation", para = "center")
        elif request.form.get('goToLocation_standby') == '前往等待區(standby)':
            mqtt_publish(command = "goToLocation", para = "standby")
        elif request.form.get('goToLocation_side') == '前往側邊(side)':
            mqtt_publish(command = "goToLocation", para = "side")
        elif request.form.get('enableMtrBrake') == '開啟電子剎車(MtrBrake)':
            mqtt_publish(command = "enableMtrBrake", para = "")
        elif request.form.get('changeHeight') == '調整桌面高度':
            try:
                robot.speaker_height = float(request.form.get("target_height"))
            except:
                robot.speaker_height = 0.0
            change_height(robot.speaker_height)
        elif request.form.get('getBatteryStatus') == '取得電池狀態':
            mqtt_publish(command = "getBatteryStatus", para = "")
        elif request.form.get('getRobotStatus_location') == '取得目前位置及方向':
            mqtt_publish(command = "getRobotStatus", para = "location")
        elif request.form.get('getRobotStatus_slam_mode') == '取得目前 SLAM 模式':
            mqtt_publish(command = "getRobotStatus", para = "slam_mode")
        elif request.form.get('getRobotStatus_power_mode') == '取得目前電源管理模式':
            mqtt_publish(command = "getRobotStatus", para = "power_mode")
        elif request.form.get('getRobotStatus_mtr_brake') == '取得目前電子剎車開關':
            mqtt_publish(command = "getRobotStatus", para = "mtr_brake")
        elif request.form.get('getRobotStatus_led_setting') == '取得目前LED顯示設定值':
            mqtt_publish(command = "getRobotStatus", para = "led_setting")
        elif request.form.get('setLight_default') == 'LED_default':
            mqtt_publish(command = "setLight", para = "default")
        elif request.form.get('setLight_customer') == 'LED_customer':
            mqtt_publish(command = "setLight", para = "customer")
        elif request.form.get('setLight_purple') == 'LED_purple':
            mqtt_publish(command = "setLight", para = "purple")
        elif request.form.get('awakeRobot') == '喚醒AMR':
            mqtt_publish(command = "awakeRobot", para = "")  
        elif request.form.get('storeData') == '儲存':
            try:
                speaker_name = request.form.get("name_data")
                speaker_height = float(request.form.get("height_data"))
            except:
                speaker_name = "None"
                speaker_height = 0.0
            store_data(speaker_name, speaker_height, robot.speaker_index)
            if(robot.speaker_index < robot.speakers_num-1):
                robot.speaker_index += 1
            else:
                robot.speaker_index = 0
        elif request.form.get('editData') == '修改':
            try:
                speaker_name = request.form.get("name_data")
                speaker_height = float(request.form.get("height_data"))
                speaker_index = int(request.form.get("index_data")) - 1
            except:
                speaker_name = "None"
                speaker_height = 0.0
                speaker_index = -1
            if(speaker_index >= 0 or speaker_index < robot.speakers_num):
                store_data(speaker_name, speaker_height, speaker_index)
        elif request.form.get('changeSpeaker1') == '切換講者1':
            robot.speaker_height = robot.speakers_datalist[0].get("height")
            change_height(robot.speaker_height)
        elif request.form.get('changeSpeaker2') == '切換講者2':
            robot.speaker_height = robot.speakers_datalist[1].get("height")
            change_height(robot.speaker_height)
        elif request.form.get('changeSpeaker3') == '切換講者3':
            robot.speaker_height = robot.speakers_datalist[2].get("height")
            change_height(robot.speaker_height)
        elif request.form.get('changeSpeaker4') == '切換講者4':
            robot.speaker_height = robot.speakers_datalist[3].get("height")
            change_height(robot.speaker_height)
        elif request.form.get('changeSpeaker5') == '切換講者5':
            robot.speaker_height = robot.speakers_datalist[4].get("height")
            change_height(robot.speaker_height)
        elif request.form.get('changeSpeaker6') == '切換講者6':
            robot.speaker_height = robot.speakers_datalist[5].get("height")
            change_height(robot.speaker_height)
        elif request.form.get('changeSpeaker7') == '切換講者7':
            robot.speaker_height = robot.speakers_datalist[6].get("height")
            change_height(robot.speaker_height)
        elif request.form.get('changeSpeaker8') == '切換講者8':
            robot.speaker_height = robot.speakers_datalist[7].get("height")
            change_height(robot.speaker_height)
        else:
            print("-----ERROR!!!-----") # unknown

    return render_template('index.html')

# Update Data ------------------------------------------------------------------------------
@app.route('/data/json')
def data_json():
    payload = {
        "time_span" : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "amr_connection" : robot.amr_connection,
        "amr_connected" : robot.amr_connected,
        # "battery_status" : robot.battery_status
        "battery_level" : robot.battery_status.get("battery_level"),
        "charging" : robot.battery_status.get("charging"),
        # "status_location" : robot.status_location,
        "location_X" : robot.status_location.get("X"),
        "location_Y" : robot.status_location.get("Y"),
        "location_orientation" : robot.status_location.get("Orientation"),
        # "status_slam_mode" : robot.status_slam_mode,
        "map_name" : robot.status_slam_mode.get("map_name"),
        "slam_mode" : robot.status_slam_mode.get("slam_mode"),
        # "status_power_mode" : robot.status_power_mode,
        "power_mode" : robot.status_power_mode.get("power_mode"),
        # "status_mtr_brake" : robot.status_mtr_brake,
        "mtr_brake" : robot.status_mtr_brake.get("mtr_brake"),
        # "status_led_setting" : robot.status_led_setting,
        "control": robot.status_led_setting.get("control"),
        "frontR": robot.status_led_setting.get("frontR"), 
        "frontG": robot.status_led_setting.get("frontG"), 
        "frontB": robot.status_led_setting.get("frontB"), 
        "frontBri": robot.status_led_setting.get("frontBri"), 
        "frontMode": robot.status_led_setting.get("frontMode"), 
        "rearMode": robot.status_led_setting.get("rearMode"), 
        "table_height" : str(robot.table_height),
        "speaker_height" : str(robot.speaker_height),
        "goToCenter_result" : robot.goToCenter_result.get("Result"),
        "goToStandby_result" : robot.goToStandby_result.get("Result"),
        "goToSide_result" : robot.goToSide_result.get("Result"),
        "mtrBrake_result" : robot.mtrBrake_result.get("Result"),
        "setLight_result" : robot.setLight_result.get("Result"),
        "speaker_index" : (robot.speaker_index+1),
        "speaker1_name": robot.speakers_datalist[0].get("name"),
        "speaker1_height": robot.speakers_datalist[0].get("height"),
        "speaker2_name": robot.speakers_datalist[1].get("name"),
        "speaker2_height": robot.speakers_datalist[1].get("height"),
        "speaker3_name": robot.speakers_datalist[2].get("name"),
        "speaker3_height": robot.speakers_datalist[2].get("height"),
        "speaker4_name": robot.speakers_datalist[3].get("name"),
        "speaker4_height": robot.speakers_datalist[3].get("height"),
        "speaker5_name": robot.speakers_datalist[4].get("name"),
        "speaker5_height": robot.speakers_datalist[4].get("height"),
        "speaker6_name": robot.speakers_datalist[5].get("name"),
        "speaker6_height": robot.speakers_datalist[5].get("height"),
        "speaker7_name": robot.speakers_datalist[6].get("name"),
        "speaker7_height": robot.speakers_datalist[6].get("height"),
        "speaker8_name": robot.speakers_datalist[7].get("name"),
        "speaker8_height": robot.speakers_datalist[7].get("height"),
    }
    return json.dumps(payload)

# MQTT FUNCTION------------------------------------------------------------------------------------------
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('/from_main')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, msg):
    #print(f"[{msg.topic}]: {msg.payload}")
    payload = msg.payload.decode('utf-8')
    message = json.loads(payload)
    print("-------msg from main-------")
    print(message)
    print("---------------------------")
    robot.amr_connection = message.get("amr_connection")
    robot.amr_connected = message.get("amr_connected")
    robot.battery_status = json.loads(str(message.get("battery_status")).replace("\'", "\""))
    robot.status_location = json.loads(str(message.get("status_location")).replace("\'", "\""))
    robot.status_slam_mode = json.loads(str(message.get("status_slam_mode")).replace("\'", "\""))
    robot.status_power_mode = json.loads(str(message.get("status_power_mode")).replace("\'", "\""))
    robot.status_mtr_brake = json.loads(str(message.get("status_mtr_brake")).replace("\'", "\""))
    robot.status_led_setting = json.loads(str(message.get("status_led_setting")).replace("\'", "\""))
    robot.table_height = message.get("table_height")
    robot.goToCenter_result = json.loads(str(message.get("goToCenter_result")).replace("\'", "\""))
    robot.goToStandby_result = json.loads(str(message.get("goToStandby_result")).replace("\'", "\""))
    robot.goToSide_result = json.loads(str(message.get("goToSide_result")).replace("\'", "\""))
    robot.mtrBrake_result = json.loads(str(message.get("mtrBrake_result")).replace("\'", "\""))
    robot.setLight_result = json.loads(str(message.get("setLight_result")).replace("\'", "\""))
    robot.have_message = True

if __name__ == '__main__':
    robot.read_file()
    #app.run('0.0.0.0', debug = True)
    app.run('192.168.69.1', debug = True)
