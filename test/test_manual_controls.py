import cv2 as cv
import libardrone.libardrone as lib_drone
import numpy as np
import asci_keys as keys

drone = lib_drone.ARDrone(True)
delay_time = int(40)  # [ms]

running = True
while running:
    key = cv.waitKey(delay_time)

    if key in [keys.a, keys.A]:
        drone.move_left()
    elif key in [keys.d, keys.D]:
        drone.move_right()
        

drone.halt()