import libardrone.libardrone as lib_drone
import asci_keys as keys
import time
import numpy as np
import cv2 as cv

class DroneController:
    flying = False
    loop_running = False
    drone_feed_window = "Drone feed"
    cycle_time = int(40)  # [ms]
    drone = None
    img_numpy = None

    def __init__(self):
        self.drone = lib_drone.ARDrone2()
        image_shape = self.drone.image_shape  # (720, 1280, 3)
        self.img_numpy = np.ones([image_shape[0], image_shape[1], image_shape[2]]) * 200 / 255.0

    def start_main_loop(self):
        print "Main loop started"
        print self.drone_feed_window
        print "Cycle time: " + str(self.cycle_time)

    def set_cycle_time(self, new_cycle_time):
        assert new_cycle_time > 0
        self.cycle_time = new_cycle_time

    def handle_key_stroke(self, key):
        if key in [keys.a, keys.A]:
            self.drone.move_left()
        elif key in [keys.d, keys.D]:
            self.drone.move_right()
        elif key in [keys.w, keys.W]:
            self.drone.move_forward()
        elif key in [keys.s, keys.S]:
            self.drone.move_backward()
        elif key in [keys.i, keys.I]:
            self.drone.move_up()
        elif key in [keys.m, keys.M]:
            self.drone.move_down()
        elif key in [keys.j, keys.J]:
            self.drone.turn_left()
        elif key in [keys.k, keys.K]:
            self.drone.turn_right()
        elif key in [keys.space]:
            if not self.flying:
                self.take_off()
            else:
                self.landing()
        elif key in [keys.backspace]:
            if not self.flying:
                self.drone.halt()
            else:
                self.landing()
                time.sleep(8)
                self.drone.halt()
            return True
        elif key is keys.esc:
            return True
        return False

    def landing(self):
        self.drone.land()
        self.flying = False

    def take_off(self):
        self.drone.takeoff()
        self.flying = True

    def update_video(self):
        self.img_numpy = self.drone.get_image()
        img_cv = cv.cvtColor(self.img_numpy, cv.COLOR_BGR2RGB)
        cv.imshow(self.drone_feed_window, img_cv)

        