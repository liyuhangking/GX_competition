import parameter
import yaml
import cv2 as cv
import numpy as np
import serailport
import tracing
import detect_task as d_t
import WiFi_Scanner

GREEN = 4

with open("config.yaml", 'r') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

Vision_Mode = config["Vision_Mode"]

def open_camera(cam_id):
    cap = cv.VideoCapture(cam_id)
    cap.set(cv.CAP_PROP_FPS, 30)
    return cap

def main(cam_id):
    cap = open_camera(cam_id)
    print("Camera Open Success!")
    while True:
        _, img = cap.read()
        img = cv.flip(img, -1)
        #模式切换1，2分别是识别物料和地标的模式位，3，4，5是不同的颜色
        if parameter.Mode.task_detect == 1:
            if parameter.Mode.color_detect == 3:
                parameter.Object_Data.color == 0x03
                d_t.Materail_detect(img,3)
            if parameter.Mode.color_detect == 4:
                parameter.Object_Data.color == 0x04
                d_t.Materail_detect(img,4)
            if parameter.Mode.color_detect == 5:
                parameter.Object_Data.color == 0x05
                d_t.Materail_detect(img,5)
            if parameter.Mode.color_detect == 0:
                d_t.Materail_detect_v2(img)

        if parameter.Mode.task_detect == 2:
            parameter.Object_Data.color == 0x04
            d_t.Land_mark_Detect(img,GREEN)

        if parameter.Mode.task_detect == 6:
            tracing.find_color_boundary(img)
        

        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    if Vision_Mode:
        cv.destroyAllWindows()

if __name__ == "__main__":
    cam_id = config["cam_id"]
    serialport_mode = config["serialport_mode"]
    
    # Wifi_Scanner_thread = threading.Thread(target=WiFi_Scanner.Wifi_Scanner_thread, args=())
    # Wifi_Scanner_thread.daemon = True  # 设置线程为守护线程，这样主程序退出时会自动结束线程
    # Wifi_Scanner_thread.start()
    
    if serialport_mode:
        serailport.Serial_Start()

    main(cam_id)
