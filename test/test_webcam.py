import cv2 as cv
import libardrone.libardrone as lib_drone
import numpy as np
import asci_keys as keys

drone = lib_drone.ARDrone(True)

drone_feed_window = "Drone feed"
delay_time = int(40)  # [ms]
image_shape = drone.image_shape  # (720, 1280, 3)
img = np.ones([image_shape[0], image_shape[1], image_shape[2]]) * 200 / 255.0

while True:
    cv.imshow(drone_feed_window, img)

    # Select action
    key = cv.waitKey(delay_time)
    if key is keys.esc:
        break
    elif key in [keys.h, keys.H]:
        print "Hello, thanks for greeting me."

    img = drone.get_image()
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    bat = drone.navdata.get(0, dict()).get('battery', 0)


drone.halt()