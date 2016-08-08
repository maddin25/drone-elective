import cv2 as cv
import libardrone.libardrone as lib_drone
import numpy as np


drone = lib_drone.ARDrone(True)

drone_feed_window = "Drone feed"
image_shape = drone.image_shape
# image_shape = (720, 1280, 3)
img = np.zeros([image_shape[0], image_shape[1], image_shape[2]])
img[:,:,0] = np.ones([image_shape[0], image_shape[1]]) * 200 / 255.0
img[:,:,1] = np.ones([image_shape[0], image_shape[1]]) * 200 / 255.0
img[:,:,2] = np.ones([image_shape[0], image_shape[1]]) * 200 / 255.0


i = 10
while i > 0:
    cv.imshow(drone_feed_window, img)
    img = drone.get_image()
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    bat = drone.navdata.get(0, dict()).get('battery', 0)
    cv.waitKey()
    i -= 1

drone.halt()