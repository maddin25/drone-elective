import libardrone.libardrone as libardrone
import time


drone = libardrone.ARDrone()
drone.reset()
# You might need to call drone.reset() before taking off if the drone is in
# emergency mode
drone.takeoff()
time.sleep(6)
drone.land()
time.sleep(8)
drone.halt()
