import libardrone.libardrone as lib_drone
import asci_keys as keys

class DroneController:
    flying = False
    loop_running = False
    drone_feed_window = "Drone feed"
    cycle_time = int(40)  # [ms]
    drone = None

    def __init__(self):
        drone = lib_drone.ARDrone2()

    def start_main_loop(self):
        print "Main loop started"
        print self.drone_feed_window
        print "Cycle time: " + str(self.cycle_time)

    def set_cycle_time(self, new_cycle_time):
        assert new_cycle_time > 0
        self.cycle_time = new_cycle_time



