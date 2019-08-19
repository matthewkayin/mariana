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

        self.check_acceleration()
        self.update_velocity(delta)
        self.handle_decceleration(delta)
        self.check_velocity()
        self.update_position(delta)

    def check_acceleration(self):
        """
        Checks to make sure acceleration hasn't exceeded max acceleration
        """

        if self.ax > self.MAX_ACC:
            self.ax = self.MAX_ACC
        elif self.ax < -self.MAX_ACC:
            self.ax = -self.MAX_ACC
        if self.ay > self.MAX_ACC:
            self.ay = self.MAX_ACC
        elif self.ay < -self.MAX_ACC:
            self.ay = -self.MAX_ACC

    def update_velocity(self, delta):
        """
        Update velocity based on acceleration
        """

        self.dx += self.ax * delta
        self.dy += self.ay * delta

    def handle_decceleration(self, delta):
        """
        If decceleration is enabled, ensure it's applied in the direction of movement
        """

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

    def check_velocity(self):
        """
        Check to make sure the velocity hasn't exceeded max velocity
        """

        if self.get_speed() > self.MAX_VEL:
            scale = self.MAX_VEL / self.get_speed()
            self.dx = scale * self.dx
            self.dy = scale * self.dy

    def update_position(self, delta):
        """
        Update the position based on velocity
        """

        self.x += self.dx * delta
        self.y += self.dy * delta

    def get_speed(self):
        return math.sqrt(self.dx ** 2 + self.dy ** 2)

    def as_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)


class Player(Entity):
    def __init__(self):
        super().__init__()

        # Set properties from base class
        self.MAX_ACC = 1
        self.DEC_SPEED = 0.2
        self.MAX_VEL = 5
        self.x = 700
        self.y = 350
        self.w = 40
        self.h = 40

        # Dash variables
        self.DASH_SPEED = 9
        self.DASH_TIME = 20
        self.is_dashing = False
        self.dash_timer = 0

        # Sprinting variables
        self.SPRINT_SPEED = 7
        self.SPRINT_ACC_MOD = 2
        self.is_sprinting = False

    def update(self, delta):
        """
        Override of the update function from Entity class
        """

        if self.dash_timer > 0:
            self.dash_timer -= delta
        if self.dash_timer > 0:
            # If the dash timer is still going, perform the modified dash update
            self.check_acceleration()
            self.check_velocity()
            self.update_position(delta)
        else:
            super().update(delta)

    def update_velocity(self, delta):
        """
        Override of the update velocity from Entity class,
        this is to increase velocity based on spring acceleration if needed
        """

        if self.is_sprinting:
            self.dx += self.ax * delta * self.SPRINT_ACC_MOD
            self.dy += self.ay * delta * self.SPRINT_ACC_MOD
        else:
            self.dx += self.ax * delta
            self.dy += self.ay * delta

    def check_velocity(self):
        """
        An override of check velocity because if the player is dashing or sprinting,
        they need to be able to go above their normal max velocity
        """

        if self.is_dashing:
            if self.get_speed() > self.DASH_SPEED:
                # Should use the same code as regular velocity cap
                scale = self.DASH_SPEED / self.get_speed()
                self.dx = scale * self.dx
                self.dy = scale * self.dy
            elif self.get_speed() <= self.MAX_VEL:
                # If our speed is at max velocity, we no longer have to use special rules
                # for velocity capping, so we can turn dashing off and use the regular check
                # velocity code
                self.is_dashing = False
                super().check_velocity()
        elif self.is_sprinting:
            if self.get_speed() > self.SPRINT_SPEED:
                # Should use the same code as regular velocity cap
                scale = self.SPRINT_SPEED / self.get_speed()
                self.dx = scale * self.dx
                self.dy = scale * self.dy
        else:
            super().check_velocity()

    def dash(self):
        """
        This function causes the player to dash in a direction equal to
        their current acceleration (joystick direction)
        """

        # Don't run this funciton if there is no axis input
        if self.ax == 0 and self.ay == 0:
            return

        hyp = math.sqrt(self.ax ** 2 + self.ay ** 2)
        self.dx = self.ax * (self.DASH_SPEED / hyp)
        self.dy = self.ay * (self.DASH_SPEED / hyp)
        self.is_dashing = True
        self.dash_timer = self.DASH_TIME


class Level():
    def __init__(self):
        """
        Default constructor, should only be ran once as the level
        will in the future be able to be given
        """

        # Initialize the player
        self.player = Player()

    def update(self, delta, input_queue, input_states):
        used_player_move_axis = False
        player_dash = False
        player_sprint = self.player.is_sprinting

        # Read the input queue
        while len(input_queue) != 0:
            event = input_queue.pop()
            if event == "AxisMoved:Axis Player Horiz" or event == "AxisMoved:Axis Player Vert":
                used_player_move_axis = True
            elif event == "ButtonDown:Fish Dash":
                player_dash = True
            elif event == "ButtonDown:Fish Sprint":
                player_sprint = True
            elif event == "ButtonUp:Fish Sprint":
                player_sprint = False

        # Perform actions based on the input queue

        # Update player acceleration
        if used_player_move_axis:
            axis_pos = [input_states["Axis Player Horiz"], input_states["Axis Player Vert"]]
            if axis_pos[0] == 0 or axis_pos[1] == 0:
                self.player.ax = self.player.MAX_ACC * axis_pos[0]
                self.player.ay = self.player.MAX_ACC * axis_pos[1]
            else:
                hyp = math.sqrt(axis_pos[0] ** 2 + axis_pos[1] ** 2)
                percentage = hyp / math.sqrt(2)
                hyp2 = self.player.MAX_ACC * percentage
                scale = hyp2 / hyp
                self.player.ax = axis_pos[0] * scale
                self.player.ay = axis_pos[1] * scale

        # Call player fish dash
        if player_dash:
            self.player.dash()

        # Update if the player is sprinting as necessary
        self.player.is_sprinting = player_sprint

        self.player.update(delta)
        print(self.player.get_speed())
