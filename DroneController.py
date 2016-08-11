import libardrone.libardrone as lib_drone
import asci_keys as keys
import time
import numpy as np
import cv2 as cv
import cv2.aruco as aruco
import os
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
        self.ref_height = 5
        self.height = 0
        self.drone.set_camera_view(True)
        self.battery_level = self.drone.navdata.get(0, dict()).get('battery', 0)
        self.marker_position = (0, 0)

        # Initialize pygame
        pygame.init()
        self.image_shape = self.drone.image_shape  # (720, 1280, 3) = (height, width, color_depth)
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
            elif event.type == pygame.KEYUP:
                self.drone.hover()
            elif event.type == pygame.KEYDOWN:
                self.turn = 0
                if event.key == pygame.K_ESCAPE:
                    self.drone.reset()
                    self.loop_running = False
                # takeoff / land
                elif event.key == pygame.K_RETURN:
                    print("return")
                    self.drone.takeoff()
                elif event.key == pygame.K_SPACE:
                    print("space")
                    self.drone.land()
                # emergency
                elif event.key in [pygame.K_BACKSPACE, pygame.K_ESCAPE]:
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
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)
        if corners:
            self.corners = corners
            dim = corners[0][0].shape
            c = np.sum(corners[0][0], axis=0) / dim[0]
            self.center = (c[0], c[1])
        else:
            self.corners = None
            self.center = None

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
        self.screen.blit(surface, (0, 0))
        pygame.display.flip()

    def pid_controller(self, pos, dt):
        pos = (0, 0)

    def plot_analysis_result(self):
        if self.corners is not None:
            self.img = aruco.drawDetectedMarkers(self.img, self.corners)
            cv.circle(self.img, self.center, 2, (0, 0, 255), 2)            cv.circle(self.img, self.center, 2, (0, 0, 255), 2)
    def print_intel(self):
        font_color = (221, 96, 22)
        font_size = 0.5
        font_weight = 1
        self.battery_level = self.drone.navdata.get(0, dict()).get('battery', 0)
        battery_text = "Battery level: {0:2.1f}%".format(self.battery_level)
        height_text = "Drone height: {0:d} mm".format(self.height)
        cv.putText(self.img, battery_text, (5, 25), cv.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_weight)
        cv.putText(self.img, height_text, (5, 55), cv.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_weight)
