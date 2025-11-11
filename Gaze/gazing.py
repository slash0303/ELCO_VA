from multiprocessing.synchronize import Event as EventObject

import cv2
from GazeTracking.gaze_tracking import GazeTracking

from eaxtension import LogE

import time as t

def use_gaze(gaze_loading_complete_flag: EventObject,
             gazing_enable_flag: EventObject,
             gazing_flag: EventObject):
    
    PROCESS_NAME = "[gaze]"
    LogE.d(PROCESS_NAME, "process started.")

    gaze = GazeTracking()
    webcam = cv2.VideoCapture(0, cv2.CAP_MSMF)
    if webcam.isOpened():
        gaze_loading_complete_flag.set()
        t.sleep(2)
        LogE.d(PROCESS_NAME, "loading complete")
    else:
        raise RuntimeError()

    enable_init_flag = True

    while True:
        if enable_init_flag:
            gazing_flag.clear()
            enable_init_flag = False

        if gazing_enable_flag.is_set():
            ret, frame = webcam.read()
            if not ret or frame is None:
                LogE.e(PROCESS_NAME, "frame is empty.")
            else:
                gaze.refresh(frame)
                
                text = "None"
                if gaze.is_right():
                    text = "Looking right"
                elif gaze.is_left():
                    text = "Looking left"
                elif gaze.is_center():
                    text = "Looking center"
                elif gaze.is_blinking():
                    text = "blinking"
                print(f"gaze: {text}", end="\r")

                if gaze.is_center() or gaze.is_blinking():
                    gazing_flag.set()
                else:
                    gazing_flag.clear()
                # cv2.imshow("gaze", frame)
                # t.sleep(0.01)
        else:
            enable_init_flag = True
        # print(f"gazing flag {gazing_enable_flag.is_set()}", end="\r")