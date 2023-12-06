import yaml
import cv2 as cv
import numpy as np
import serailport
import detect_task as d_t

with open("config.yaml", 'r') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

def main(cam_id):
    d_t.select_mode(cam_id)

if __name__ == "__main__":
    cam_id = config["cam_id"]
    serialport_mode = config["serialport_mode"]
    
    # Wifi_Scanner_thread = threading.Thread(target=WiFi_Scanner.Wifi_Scanner_thread, args=())
    # Wifi_Scanner_thread.daemon = True  # 设置线程为守护线程，这样主程序退出时会自动结束线程
    # Wifi_Scanner_thread.start()
    
    if serialport_mode:
        serailport.Serial_Start()
    

    main(cam_id)


