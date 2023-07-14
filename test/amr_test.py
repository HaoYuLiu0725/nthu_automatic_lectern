#!/usr/bin/env python3
# coding: utf-8
from AMR import AMR

def main():
    amr = AMR()
    if amr.connect(3) == 1: # 連線成功
        while True:
            try:
                command = input("請輸入指令(status / ls map / ls loc / sw map / shutdown / q): ")
                if command == "status":
                    print("[getRobotStatus]: please enter command to get robot status:")
                    print("(location / battery_level / charging / speed_level / ang_speed_level / error / warning / slam_mode / sleep_mode_setting / led_setting)")
                    cmd = input()
                    print(amr.getRobotStatus(cmd))
                elif command == "ls map":
                    print(amr.listMap())
                elif command == "ls loc":
                    print(amr.listLocation())
                elif command == "sw map":
                    mapName = input("[getRobotStatus]: please enter map name to switch: ")
                    print(amr.switchMap(mapName))
                elif command == "shutdown":
                    print(amr.shutdown())
                elif command == "q" :
                    quit()
                else:
                    print(f"\nError! '{command}' is not recognized or not supported!")

            except Exception as e:
                print(str(e))


if __name__ == "__main__":
    main()