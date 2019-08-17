# Mariana
# Code - Matt Madden
# level.py -- Logic for actual gameplay goes here

import pygame
import math


class Entity():
    """
    Holds a template for all moving objects in game
    """
    def __init__(self):
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.dx = 0
        self.dy = 0
        self.MAX_VEL = 0
        self.ax = 0
        self.ay = 0
        self.MAX_ACC = 0
        self.DEC_SPEED = 0

    def update(self, delta):
        """
        Update the entity position once per frame based on speed / acceleration
        """

        # Check to make sure acceleration hasn't been set to be higher than max acceleration
        if self.ax > self.MAX_ACC:
            self.ax = self.MAX_ACC
        elif self.ax < -self.MAX_ACC:
            self.ax = -self.MAX_ACC
        if self.ay > self.MAX_ACC:
            self.ay = self.MAX_ACC
        elif self.ay < -self.MAX_ACC:
            self.ay = -self.MAX_ACC

        # Update velocity based on acceleration
        self.dx += self.ax * delta
        self.dy += self.ay * delta

        # Handle any decceleration
        if self.DEC_SPEED != 0:
            if self.dx > 0:
                self.dx -= (self.DEC_SPEED / self.get_speed()) * self.dx * delta
                # This is so that decceleration stops the entity eventually rather than
                # bouncing between decceleration in two directions endlessly
                if self.ax == 0 and self.dx < 0:
                    self.dx = 0
            elif self.dx < 0:
                self.dx -= (self.DEC_SPEED / self.get_speed()) * self.dx * delta
                if self.ax == 0 and self.dx > 0:
                    self.dx = 0
            if self.dy > 0:
                self.dy -= (self.DEC_SPEED / self.get_speed()) * self.dy * delta
                if self.ay == 0 and self.dy < 0:
                    self.dy = 0
            elif self.dy < 0:
                self.dy -= (self.DEC_SPEED / self.get_speed()) * self.dy * delta
                if self.ay == 0 and self.dy > 0:
                    self.dy = 0

        # Check to make sure velocity hasn't exceeded max velocity
        if self.get_speed() > self.MAX_VEL:
            scale = self.MAX_VEL / self.get_speed()
            self.dx = scale * self.dx
            self.dy = scale * self.dy

        # Update the position based on velocity
        self.x += self.dx * delta
        self.y += self.dy * delta

    def get_speed(self):
        return math.sqrt(self.dx ** 2 + self.dy ** 2)

    def as_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)


class Level():
    def __init__(self):
        """
        Default constructor, should only be ran once as the level
        will in the future be able to be given
        """

        # Initialize the player
        self.player = Entity()
        self.player.MAX_ACC = 1
        self.player.DEC_SPEED = 0.2
        self.player.MAX_VEL = 5
        self.player.x = 700
        self.player.y = 350
        self.player.w = 40
        self.player.h = 40

    def handle_event(self, event, state_info=None):
        """
        Handle an input from the main class, input event names are as follows
        AxisMoved:<AXIS NAME>
        ButtonDown:<BUTTON NAME>
        ButtonUp:<BUTTON NAME>
        """
        if event == "AxisMoved:Axis Player Horiz" or event == "AxisMoved:Axis Player Vert":
            if state_info[0] == 0 or state_info[1] == 0:
                self.player.ax = self.player.MAX_ACC * state_info[0]
                self.player.ay = self.player.MAX_ACC * state_info[1]
            else:
                hyp = math.sqrt(state_info[0] ** 2 + state_info[1] ** 2)
                percentage = hyp / math.sqrt(2)
                hyp2 = self.player.MAX_ACC * percentage
                scale = hyp2 / hyp
                self.player.ax = state_info[0] * scale
                self.player.ay = state_info[1] * scale

    def update(self, delta):
        self.player.update(delta)
