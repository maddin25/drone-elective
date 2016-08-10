import libardrone.libardrone as lib_drone
import asci_keys as keys
import time
import numpy as np
import cv2 as cv
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

    def __init__(self, use_webcam=False):
        self.use_webcam = use_webcam
        if self.use_webcam:
            self.cam = cv.VideoCapture(0)
        self.drone = lib_drone.ARDrone2(hd=True)
        self.drone.set_camera_view(True)
        self.battery_level = self.drone.navdata.get(0, dict()).get('battery', 0)
        print "Battery level: {0:2.1f}%".format(self.battery_level)

        # Initialize pygame
        pygame.init()
        self.image_shape = self.drone.image_shape  # (720, 1280, 3) = (height, width, color_depth)
        self.screen = pygame.display.set_mode((self.image_shape[1], self.image_shape[0]))  # width, height
        self.img_numpy = np.zeros([self.image_shape[0], self.image_shape[1], self.image_shape[2]])
        self.img_manuals = pygame.image.load(os.path.join("media", "commands.png")).convert()
        self.screen.blit(self.img_manuals, (0, 0))
        pygame.display.flip()

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
        pass


    def land(self):
        self.drone.land()
        self.flying = False

    def take_off(self):
        self.drone.takeoff()
        self.flying = True

    def update_video_from_drone(self):
        self.img_numpy = self.drone.get_image()  # (360, 640, 3) or (720, 1280, 3)
        # print "Received image with dimensions ", self.img_numpy.shape
        # print "Min, max values:", np.amin(self.img_numpy), np.amax(self.img_numpy)
        self.show_np_array(self.img_numpy, -90)

    def update_video_from_webcam(self):
        ret, frame = self.cam.read()
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        self.img_numpy = np.asarray(frame)
        self.show_np_array(self.img_numpy, -90)

    def show_np_array(self, array, rotate=0):
        surface = pygame.surfarray.make_surface(array)
        surface = pygame.transform.rotate(surface, rotate)
        # print "Surface size: ", surface.get_size()
        self.screen.blit(surface, (0, 0))
        pygame.display.flip()
