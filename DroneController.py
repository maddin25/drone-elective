import libardrone.libardrone as lib_drone
import asci_keys as keys
import time
import numpy as np
import cv2 as cv
import cv2.aruco as aruco
import os
import math
import pygame
import pygame.surfarray


class DroneController:
    flying = False
    loop_running = True
    drone_feed_window = "Drone feed"
    cycle_time = int(40)  # [ms]
    nr_cycles_no_key_pressed = 0
    view_front_camera = True
    turn = 0
    automatic_mode = False
    center = None
    corners = None

    def __init__(self, use_webcam=False):
        self.use_webcam = use_webcam
        if self.use_webcam:
            self.cam = cv.VideoCapture(0)
        self.drone = lib_drone.ARDrone2(hd=True)
        time.sleep(1)
        self.time = time.time()
        self.integral = {"err_x": 0, "err_height": 0, "err_distance": 0}
        self.last = {"err_x": 0, "err_height": 0, "err_distance": 0}
        self.control = {"x": 0, "height": 0, "distance": 0}
        self.K = {"P": 1, "I": 1, "D": 1}
        self.ref_height = 800  # [mm]
        self.height = 0  # [mm]
        self.drone.set_camera_view(True)
        self.battery_level = self.drone.navdata.get(0, dict()).get('battery', 0)
        self.marker_position = (0, 0)

        # Initialize pygame
        pygame.init()
        self.image_shape = self.drone.image_shape  # (720, 1280, 3) = (height, width, color_depth)
        self.marker_size = 0
        self.ref_marker_size = math.sqrt(35000)  # TODO: set value
        self.img = np.array([1], ndmin=3)
        self.screen = pygame.display.set_mode((self.image_shape[1], self.image_shape[0]))  # width, height
        self.img_manuals = pygame.image.load(os.path.join("media", "commands.png")).convert()
        self.screen.blit(self.img_manuals, (0, 0))
        pygame.display.flip()

        # Initialize aruco
        self.aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
        self.parameters = aruco.DetectorParameters_create()

        print "Drone initialized"

    def start_main_loop(self):
        print "Main loop started"
        while self.loop_running:
            dt = time.time() - self.time
            self.time = time.time()
            self.handle_key_stroke()
            if not self.use_webcam:
                self.update_video_from_drone()
            else:
                self.update_video_from_webcam()
            self.analyze_image()
            self.refresh_img(self.img, -90)

        self.drone.halt()

    def set_cycle_time(self, new_cycle_time):
        assert new_cycle_time > 0
        self.cycle_time = new_cycle_time

    def handle_key_stroke(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.loop_running = False
                self.drone.halt()
            elif event.type == pygame.KEYUP:
                self.drone.hover()
            elif event.type == pygame.KEYDOWN:
                self.turn = 0
                if event.key in [pygame.K_BACKSPACE, pygame.K_ESCAPE]:
                    self.drone.halt()
                    self.loop_running = False
                # takeoff / land
                elif event.key == pygame.K_RETURN:
                    print("return")
                    self.drone.takeoff()
                elif event.key == pygame.K_SPACE:
                    print("space")
                    self.drone.land()
                elif event.key == pygame.K_r:
                    self.drone.reset()
                # activate program modes
                elif event.key == pygame.K_t:
                    self.automatic_mode = not self.automatic_mode
                # video
                elif event.key == pygame.K_v:
                    self.view_front_camera = not self.view_front_camera
                    self.drone.set_camera_view(self.view_front_camera)
                elif self.automatic_mode:
                    continue
                # forward / backward
                elif event.key == pygame.K_w:
                    self.drone.move_forward()
                elif event.key == pygame.K_s:
                    self.drone.move_backward()
                # left / right
                elif event.key == pygame.K_a:
                    self.drone.move_left()
                elif event.key == pygame.K_d:
                    self.drone.move_right()
                # up / down
                elif event.key == pygame.K_UP:
                    self.drone.move_up()
                elif event.key == pygame.K_DOWN:
                    self.drone.move_down()
                # turn left / turn right
                elif event.key == pygame.K_LEFT:
                    self.drone.turn_left()
                    self.turn = +1
                elif event.key == pygame.K_RIGHT:
                    self.drone.turn_right()
                    self.turn = -1
                # speed
                elif event.key == pygame.K_1:
                    self.drone.speed = 0.1
                elif event.key == pygame.K_2:
                    self.drone.speed = 0.2
                elif event.key == pygame.K_3:
                    self.drone.speed = 0.3
                elif event.key == pygame.K_4:
                    self.drone.speed = 0.4
                elif event.key == pygame.K_5:
                    self.drone.speed = 0.5
                elif event.key == pygame.K_6:
                    self.drone.speed = 0.6
                elif event.key == pygame.K_7:
                    self.drone.speed = 0.7
                elif event.key == pygame.K_8:
                    self.drone.speed = 0.8
                elif event.key == pygame.K_9:
                    self.drone.speed = 0.9
                elif event.key == pygame.K_0:
                    self.drone.speed = 1.0
        # After parsing the input events
        if self.turn > 0 and not self.automatic_mode:
            print "Continue rotating left"
            self.drone.turn_left()
        elif self.turn < 0 and not self.automatic_mode:
            print "Continue rotating right"
            self.drone.turn_right()

    def analyze_image(self):
        gray = cv.cvtColor(self.img, cv.COLOR_RGB2GRAY)
        all_corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)
        if all_corners:
            self.corners = all_corners
            corners = all_corners[0][0]
            dim = corners.shape
            c = np.sum(corners, axis=0) / dim[0]
            self.center = (c[0], c[1])
            x1, y1 = corners[0][0], corners[0][1]
            x2, y2 = corners[1][0], corners[1][1]
            x3, y3 = corners[2][0], corners[2][1]
            x4, y4 = corners[3][0], corners[3][1]
            self.marker_size = abs((x3 - x1) * (y4 - y2) + (x4 - x2) * (y1 - y3)) / 2
            # A = (1 / 2) | [(x3 - x1)(y4 - y2) + (x4 - x2)(y1 - y3)] |
        else:
            self.corners = None
            self.center = None
            self.marker_size = 0

    def highlight_marker(self):
        pass

    def land(self):
        self.drone.land()
        self.flying = False

    def take_off(self):
        self.drone.takeoff()
        self.flying = True

    def update_video_from_drone(self):
        self.img = self.drone.get_image()  # (360, 640, 3) or (720, 1280, 3)
        self.plot_analysis_result()

    def update_video_from_webcam(self):
        ret, self.img = self.cam.read()
        self.img = cv.cvtColor(self.img, cv.COLOR_BGR2RGB)
        self.plot_analysis_result()

    def refresh_img(self, array, rotate=0):
        surface = pygame.surfarray.make_surface(array)
        surface = pygame.transform.rotate(surface, rotate)
        surface = pygame.transform.flip(surface, True, False)
        self.screen.blit(surface, (0, 0))
        pygame.display.flip()

    def pid_controller(self, marker_center, height, marker_size, dt):
        err_x = marker_center[0] / self.image_shape[1] - 0.5
        err_height = height - self.ref_height
        err_distance = marker_size - self.ref_marker_size
        # Calculate the integral parts
        self.integral["err_x"] += err_x
        self.integral["err_height"] += err_height
        self.integral["err_distance"] += err_distance
        # Calculate new control values
        self.control["x"] = self.K["P"] * err_x \
                          + self.K["I"] * self.integral["err_x"] \
                          + self.K["D"] * (err_x - self.last["err_x"])
        self.control["height"] = self.K["P"] * err_height \
                            + self.K["I"] * self.integral["err_height"] \
                            + self.K["D"] * (err_height - self.last["err_height"])
        self.control["distance"] = self.K["P"] * err_distance \
                            + self.K["I"] * self.integral["err_distance"] \
                            + self.K["D"] * (err_distance - self.last["err_distance"])
        # Save values for the next iteration
        self.last["err_x"] = err_x
        self.last["err_height"] = err_height
        self.last["err_distance"] = err_distance

    def plot_analysis_result(self):
        if self.corners is not None:
            self.img = aruco.drawDetectedMarkers(self.img, self.corners)
            cv.circle(self.img, self.center, 2, (0, 0, 255), 2)

    def print_intel(self):
        font_color = (0, 0, 0)
        font_size = 0.5
        font_weight = 1.5
        self.battery_level = self.drone.navdata.get(0, dict()).get('battery', 0)
        battery_text = "Battery level: {0:2.1f}%".format(self.battery_level)
        height_text = "Drone height: {0:d} mm".format(self.height)
        marker_size_text = "Marker size: {0:.1f} x10^3 px^2".format(self.marker_size / 1000)
        cv.putText(self.img, battery_text, (5, 25), cv.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_weight)
        cv.putText(self.img, height_text, (5, 55), cv.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_weight)
        cv.putText(self.img, marker_size_text, (5, 85), cv.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_weight)

