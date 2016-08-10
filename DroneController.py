import libardrone.libardrone as lib_drone
import asci_keys as keys
import time

class DroneController:
    flying = False
    loop_running = False
    drone_feed_window = "Drone feed"
    cycle_time = int(40)  # [ms]
    drone = None

    def __init__(self):
        self.drone = lib_drone.ARDrone2()

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
                self.drone.takeoff()
                self.flying = True
            else:
                self.drone.land()
                self.flying = False
        elif key in [keys.backspace]:
            if not self.flying:
                self.drone.halt()
            else:
                self.drone.land()
                self.flying = False
                time.sleep(8)
                self.drone.halt()
            return True
        elif key is keys.esc:
            return True
        return False

