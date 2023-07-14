#!/usr/bin/env python3
# coding: utf-8
import json
import socket
from datetime import datetime

class AMR:
    def __init__(self):
        self.host = "192.168.168.168"
        self.commandPort = 8900
        self.listenerPort = 8901
        self.commandClient = None
        self.listenerClient = None
        self.currentIp = ""

    def getIp(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

    def connect(self, retry: int):
        """
        建立連線
        <param> retry(int): 重新建立連線次數
        :return: 連線狀態
        """
        result = 0
        retryCount = 0
        connected = False
        while not connected:
            try:
                print(datetime.now(), " 嘗試建立連線中(Command)...")
                self.commandClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.commandClient.settimeout(1)
                self.commandClient.connect((self.host, self.commandPort))
                print(datetime.now(), " 連線成功!(Command)")
                connected = True
                result = 1

            except socket.timeout:
                retryCount = retryCount + 1
                if retryCount < retry:
                    print(datetime.now(), " 連線timeout! 重新連線...")
                    pass
                else:
                    print(datetime.now(), " 連線timeout! 停止嘗試!")
                    break

        return result

    def disconnect(self):
        """
        關閉連線
        :return: 關閉狀態
        """
        result = 0
        try:
            self.commandClient.close()
            self.listenerClient.close()
            result = 1
        except Exception as e:
            print(e)
        finally:
            return result

    def __sendCommand(self, command):
        """
        發送指令
        <param> command(any/dict): 要發送的JSON格式的指令
        :return: 發送指令狀態 / AMR的回覆
        """
        print(datetime.now(), " 收到指令: ", command)
        result = 0
        command = json.dumps(command)
        try:
            self.commandClient.settimeout(10)
            print("set timeout complete")
            self.commandClient.sendall(command.encode())
            print("send command complete")
            result = str(self.commandClient.recv(2048), encoding='utf-8')
            print("get result complete")
        except socket.timeout:
            print("指令timeout")
            result = -1
        except Exception as e:
            print(e)
            result = 0
        finally:
            self.commandClient.settimeout(None)
            return result

    # GetRobotStatus #
    def getRobotStatus(self, param: str):
        """
        取得目前機體狀態
        <param> param(str): 指定欲取得的資料
            "location": AMR 目前位置及方向
            "battery_level": 目前電量
            "charging": 是否充電中
            "speed_level": 移動速度
            "ang_speed_level": 旋轉速度
            "error": 目前是否存在錯誤事件 
            "warning": 目前是否存在警告事件
            "slam_mode": 目前 SLAM 模式
            "power_mode": 目前電源管理模式
            "sleep_mode_setting": 目前睡眠模式設定
            "led_setting": 目前 LED 顯示設定值 
            "mtr_brake": 目前電子剎車開關。
        :return: AMR的回覆
        """
        command = {
            "Command": "GetRobotStatus",
            "Para": param
        }
        return self.__sendCommand(command)

    # SetMap #
    def getMap(self, mapName: str = None):
        """
        取得地圖資訊
        <param> mapName(str): 地圖名稱
            地圖名稱允許帶入空字串，表示取得當下運行地圖
        :return: AMR的回覆
        """
        command = {
            "Command": "SetMap",
            "Para": "get",
            "MapName": "" if mapName is None else mapName
        }
        return self.__sendCommand(command)
    
    def saveMap(self, mapName: str):
        """
        保存地圖
        <param> mapName(str): 地圖名稱
        :return: AMR的回覆
        """
        command = {
            "Command": "SetMap",
            "Para": "save",
            "MapName": mapName
        }
        return self.__sendCommand(command)

    def deleteMap(self, mapName: str):
        """
        刪除地圖
        <param> mapName(str): 地圖名稱
        :return: AMR的回覆
        """
        command = {
            "Command": "SetMap",
            "Para": "delete",
            "MapName": mapName
        }
        return self.__sendCommand(command)

    def listMap(self):
        """
        取得目前地圖列表
        :return: AMR的回覆
        """
        command = {
            "Command": "SetMap",
            "Para": "list"
        }
        return self.__sendCommand(command)

    # GetBatteryStatus #
    def getBatteryStatus(self):
        """
        取得目前電量、是否充電中
        :return: AMR的回覆
        """
        command = {
            "Command": "GetBatteryStatus"
        }
        return self.__sendCommand(command)
    
    # SwitchMode #
    def switchMode(self, mode: str, mapName: str = None):
        """
        切換模式(建圖模式 / 導航模式)
        <param> mode(str): 模式
            "mapping": 建圖模式，地圖持續更新修正
            "localization": 導航定位模式，地圖不更新 
        <param> mapName(str): 地圖名稱
            1.切換建圖模式，可選擇特定地圖繼續建圖; 也可選擇不輸入，等同於重新建立一張新地圖\n
            2.切換導航定位模式，必須選擇特定地圖。
        :return: AMR的回覆
        """
        command = {
            "Command": "SwitchMode",
            "Mode": mode,
            "MapName": "" if mapName is None else mapName
        }
        return self.__sendCommand(command)
    
    def makeNewMap(self):
        """
        製作新的地圖
        :return: AMR的回覆
        """
        return self.switchMode("mapping")
    
    def switchMap(self, mapName: str):
        """
        切換地圖
        <param> mapName(str): 地圖名稱
        :return: AMR的回覆
        """
        return self.switchMode("localization", mapName)

    # ManualControl #
    def manualControl(self, order: str):
        """
        遙控移動
        <param> order(str): 指令
            移動方式：
                "F": 前進
                "FL": 前進+左轉
                "FR": 前進+右轉
                "B": 倒退
                "BL": 倒退+左轉
                "BR": 倒退+右轉
                "L": 原地左轉
                "R": 原地右轉
                "S": 停止
        :return: AMR的回覆
        """
        command = {
            "Command": "ManualControl",
            "Para": order
        }
        return self.__sendCommand(command)

    # GoCharge #
    def goCharge(self, chargerName: str = "Default"):
        """
        指揮AMR回充電座充電, 可指定充電座
        <param> chargerName(str): 充電座名稱
            未輸入此參數，則回與裝置距離最相近的充電座(已記錄)
        :return: AMR的回覆
        """
        command = {
            "Command": "GoCharge",
            "Name": chargerName
        }
        return self.__sendCommand(command)
    
    # GoToXY #
    def goToXY(self, x: int = 0, y: int = 0, orientation: float = -1):
        """
        移動到指定座標
        <param> x(int): 指定地圖的X座標(mm)
        <param> y(int): 指定地圖的Y座標(mm)\n
        <param> orientation(double): 
            指定:朝向角度(0 ≤ Orientation < 360)
            不指定: -1
        :return: AMR的回覆
        """
        command = {
            "Command": "GoToXY",
            "X": x,
            "Y": y,
            "Orientation": orientation
        }
        return self.__sendCommand(command)
    
    # GoToTarget #
    def goToTarget(self, distance: int = 0, orientation: float = 0):
        """
        移動指定距離、角度
        <param> distance(int): 移動距離(mm) [正值:前進;負值:後退]
        <param> orientation(double): 旋轉角度，角度範圍 -180 ~ 180 度 [正值:逆時針旋轉;負值:順時針旋轉]
        :return: AMR的回覆
        """
        command = {
            "Command": "GoToTarget",
            "Distance": distance,
            "Orientation": orientation
        }
        return self.__sendCommand(command)
    
    def turn(self, angle: float):
        """
        調整水平角度
        <param> angle: 水平角度(-180 ~ 180 度)
        :return: AMR的回覆
        """
        return self.goToTarget(0, angle)

    # GoToLocation #
    def goToLocation(self, locationName: str):
        """
        移動到已儲存的指定地點
        <param> locationName(str): 欲前往的地點名稱
        :return: AMR的回覆
        """
        command = {
            "Command": "GoToLocation",
            "Name": locationName
        }
        return self.__sendCommand(command)

    # SetSpeedLevel #
    def setSpeedLevel(self, level: int):
        """
        設定AMR前進時的移動速度, 後退的速度固定為 0.2 m/s\n
        <param> level(int):
            1: 0.2 m/s
            2: 0.4 m/s
            3: 0.6 m/s
            4: 0.8 m/s
            5: 1.0 m/s
        :return: AMR的回覆
        """
        command = {
            "Command": "SetSpeedLevel",
            "Para": level
        }
        return self.__sendCommand(command)

    # SetLight #
    def setLight(self, frontR: int = 255, frontG: int = 255, frontB: int = 255, 
                    frontBri: int = 255, frontMode: int = 1, rearMode: int = 0):
        """
        設定燈條顏色與閃爍模式
        <param> frontR(int): 0 ~ 255
        <param> frontG(int): 0 ~ 255
        <param> frontB(int): 0 ~ 255
        <param> frontBri(int): 0 ~ 255
        <param> frontMode(int): 前燈條閃爍方式 0 ~ 7 
                                0: 前車燈全暗
                                1: 前車燈恆亮
                                2: 前車燈一般閃爍
                                3: 前車燈快速閃爍
                                4: 前車燈由左至右依序閃爍
                                5: 前車燈由右至左依序閃爍
                                6: 前車燈由中間至兩邊依序閃爍
                                7: 前車燈由兩邊至中間依序閃爍
        <param> rearMode(int): 後燈條閃爍方式 0 ~ 3
                                0: 後車燈全暗
                                1: 後車燈恆亮
                                2: 後車燈一般閃爍
                                3: 後車燈快速閃爍
        :return: AMR的回覆
        """
        command = {
            "Command": "SetLight",
            "frontR": frontR,
            "frontG": frontG,
            "frontB": frontB,
            "frontBri": frontBri,
            "frontMode": frontMode,
            "rearMode": rearMode,
        }
        return self.__sendCommand(command)

    # SetLocation #
    def addLocation(self, locationName: str = "Default", locationType: str = "landMark", 
                            x: int = None, y: int = None, orientation: float = None):
        """
        新增地點(保存地點)
        <param> locationName(str): 地點名稱
        <param> locationType(str): "charger": 充電座 ; "landMark": 預設
        <param> x(int): 指定地圖的X座標(mm)
        <param> y(int): 指定地圖的Y座標(mm)\n
        <param> orientation(double): 
            指定:朝向角度(0 ≤ Orientation < 360)
            不指定: -1
        <special case>
            自動讀取機器位置與角度後儲存: x = 0, y = 0, orientation = -1
            自動讀取機器位置但不儲存角度: x = 0, y = 0, orientation = -2
            自訂機器位置但不儲存角度: x = any, y = any, orientation = -4
        :return: AMR的回覆
        """
        X = 0 if x is None else x
        Y = 0 if y is None else y
        O = -1 if orientation is None else orientation
        command = {
            "Command": "SetLocation",
            "Para": "add",
            "Name": locationName,
            "Type": locationType,
            "X": X,
            "Y": Y,
            "Orientation": O
        }
        return self.__sendCommand(command)

    def saveCurrentLocation(self, locationName: str = "Default"):
        """
        紀錄並儲存目前AMR的位置, 自動讀取機器位置與角度
        <param> locationName(str): 地點名稱
        :return: AMR的回覆
        """
        command = {
            "Command": "SetLocation",
            "Para": "add",
            "Name": locationName,
            "Type": "landMark",
            "X": 0,
            "Y": 0,
            "Orientation": -1
        }
        return self.__sendCommand(command)
    
    def saveCurrentCharger(self, chargerName: str = "Default"):
        """
        紀錄並儲存目前AMR的位置作為充電座, 自動讀取機器位置與角度
        <param> chargerName(str): 充電座名稱
        :return: AMR的回覆
        """
        command = {
            "Command": "SetLocation",
            "Para": "add",
            "Name": chargerName,
            "Type": "charger",
            "X": 0,
            "Y": 0,
            "Orientation": -1
        }
        return self.__sendCommand(command)
    
    def deleteLocation(self, locationName: str):
        """
        刪除地點
        <param> locationName: 地點名稱
        :return: AMR的回覆
        """
        command = {
            "Command": "SetLocation",
            "Para": "delete",
            "Name": locationName
        }
        return self.__sendCommand(command)
    
    def listLocation(self):
        """
        取得地點列表
        :return: AMR的回覆
        """
        command = {
            "Command": "SetLocation",
            "Para": "list"
        }
        return self.__sendCommand(command)
    
    def saveAllLocation(self, mapName: str):
        """
        儲存當前載入地圖的所有地點，需帶入當前載入地圖名稱
        <param> mapName(str): 當前載入地圖名稱
        :return: AMR的回覆
        """
        command = {
            "Command": "SetLocation",
            "Para": "save",
            "MapName": mapName
        }
        return self.__sendCommand(command)
    
    # SetAngSpeedLevel #
    def setAngSpeedLevel(self, level: int):
        """
        切換旋轉速度
        <param> level(int):
            1: 0.400 rad/s
            2: 0.985 rad/s
            3: 1.570 rad/s
        :return: AMR的回覆
        """
        command = {
            "Command": "SetAngSpeedLevel",
            "Para": level
        }
        return self.__sendCommand(command)
    
    # SetPowerMode #
    def setPowerMode(self, mode: str):
        """
        主動切換電源管理模式。
        <param> mode(str):
            "lightSleep": 進入睡眠模式。
            "sleep": 進入深眠模式。
            "normal": 進入一般模式。
        注意事項：
            (1) 如果已經進入該模式,再次帶入一樣的Mode參數,則會失敗。
            (2) 如果已經設置睡眠、深眠其中之一,無論成功或失敗,必須先喚醒AMR01才能再互相切換睡眠、深眠 。
            (3) 睡眠模式達條件會預設自動進入,如果需要修改進入條件,請參考SetSleepMode 。
        :return: AMR的回覆
        """
        command = {
            "Command": "SetPowerMode",
            "Mode": mode
        }
        return self.__sendCommand(command)

    # Shutdown #
    def shutdown(self):
        """
        使AMR關機
        :return: AMR的回覆
        """
        command = {
            "Command": "Shutdown",
            "Para": ""
        }
        return self.__sendCommand(command)
    
    # Reboot #
    def reboot(self):
        """
        使AMR重新開機
        :return: AMR的回覆
        """
        command = {
            "Command": "Reboot",
            "Para": ""
        }
        return self.__sendCommand(command)
    
    # EMS #
    def EMS(self):
        """
        使機器進行軟體上的緊急停止
        :return: AMR的回覆
        """
        command = {
            "Command": "EMS",
            "Para": ""
        }
        return self.__sendCommand(command)

    # Relocate #
    def relocateByLocation(self, locationName: str):
        """
        給已設定地點的名稱，並且在此座標內五公尺重新定位。
        <param> locationName(str): 已設定地點的名稱
        :return: AMR的回覆
        """
        command = {
            "Command": "Relocate",
            "Para":"loc",
            "Name": locationName
        }
        return self.__sendCommand(command)
    
    # MtrBrake #
    def MtrBrake(self, param):
        """
        開關電子剎車，以下狀況無法執行：
        1. 馬達異常。
        2. SPI通訊異常。
        3. 功能未支援。\n
        <param> param(str): 
            "On": 開啟
            "Off": 關閉
        :return: AMR的回覆
        """
        command = {
            "Command": "MtrBrake",
            "Para": param
        }
        return self.__sendCommand(command)
