# Mariana
# Code - Matt Madden
# entities.py -- Module for game entities

import math
import pygame


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

        self.check_acceleration(self.MAX_ACC)
        self.update_velocity(self.ax, self.ay, delta)
        self.handle_decceleration(self.DEC_SPEED, delta)
        self.check_velocity(self.MAX_VEL)
        self.update_position(self.dx, self.dy, delta)

    def check_acceleration(self, max_accel):
        """
        Checks to make sure acceleration hasn't exceeded max acceleration
        """

        if self.ax > max_accel:
            self.ax = max_accel
        elif self.ax < -max_accel:
            self.ax = -max_accel
        if self.ay > max_accel:
            self.ay = max_accel
        elif self.ay < -max_accel:
            self.ay = -max_accel

    def update_velocity(self, x_accel, y_accel, delta):
        """
        Update velocity based on x and y acceleration
        """

        self.dx += x_accel * delta
        self.dy += y_accel * delta

    def handle_decceleration(self, deccel_speed, delta):
        """
        If decceleration is enabled, ensure it's applied in the direction of movement
        """

        if deccel_speed != 0:
            if self.dx > 0:
                self.dx -= (deccel_speed / self.get_speed()) * self.dx * delta
                # This is so that decceleration stops the entity eventually rather than
                # bouncing between decceleration in two directions endlessly
                if self.ax == 0 and self.dx < 0:
                    self.dx = 0
            elif self.dx < 0:
                self.dx -= (deccel_speed / self.get_speed()) * self.dx * delta
                if self.ax == 0 and self.dx > 0:
                    self.dx = 0
            if self.dy > 0:
                self.dy -= (deccel_speed / self.get_speed()) * self.dy * delta
                if self.ay == 0 and self.dy < 0:
                    self.dy = 0
            elif self.dy < 0:
                self.dy -= (deccel_speed / self.get_speed()) * self.dy * delta
                if self.ay == 0 and self.dy > 0:
                    self.dy = 0

    def check_velocity(self, max_vel):
        """
        Check to make sure the velocity hasn't exceeded max velocity
        """

        if self.get_speed() > max_vel:
            scale = max_vel / self.get_speed()
            self.dx = scale * self.dx
            self.dy = scale * self.dy

    def update_position(self, x_vel, y_vel, delta):
        """
        Update the position based on velocity
        """

        self.x += x_vel * delta
        self.y += y_vel * delta

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
        self.w = 20
        self.h = 36

        # Dash variables
        self.DASH_SPEED = 9
        self.DASH_TIME = 20
        self.DASH_DEC_MOD = 3
        self.can_dash = True
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
            self.check_acceleration(self.MAX_ACC)
            self.check_velocity(self.MAX_VEL)
            self.update_position(self.dx, self.dy, delta)
        else:
            super().update(delta)

    def update_velocity(self, x_accel, y_accel, delta):
        """
        Override of the update velocity from Entity class,
        this is to increase velocity based on spring acceleration if needed
        """

        if self.is_sprinting:
            super().update_velocity(x_accel * self.SPRINT_ACC_MOD, y_accel * self.SPRINT_ACC_MOD, delta)
        else:
            super().update_velocity(x_accel, y_accel, delta)

    def handle_decceleration(self, deccel_speed, delta):
        """
        Override of update velocity that enables faster decceleration from higher speed
        states like dashing or sprinting
        """

        if self.is_dashing and self.dash_timer <= 0:
            self.dash_timer -= delta
            extra_deccel = (-1 * self.dash_timer) / 10
            super().handle_decceleration(deccel_speed * self.DASH_DEC_MOD * extra_deccel, delta)
        else:
            super().handle_decceleration(deccel_speed, delta)

    def check_velocity(self, max_vel):
        """
        An override of check velocity because if the player is dashing or sprinting,
        they need to be able to go above their normal max velocity
        """

        if self.is_dashing:
            if self.get_speed() > self.DASH_SPEED:
                super().check_velocity(max_vel)
            elif self.get_speed() <= max_vel:
                # If we are dashing but our speed has gone into the max vel range, that means
                # we can return the player to regular movement
                self.is_dashing = False
                super().check_velocity(max_vel)
        elif self.is_sprinting:
            super().check_velocity(self.SPRINT_SPEED)
        else:
            super().check_velocity(max_vel)

    def dash(self):
        """
        This function causes the player to dash in a direction equal to
        their current acceleration (joystick direction)
        """

        # This is so that the player must repress the dash button in order to dash twice
        if not self.can_dash:
            return

        # Don't run this funciton if there is no axis input
        if self.ax == 0 and self.ay == 0:
            return

        hyp = math.sqrt(self.ax ** 2 + self.ay ** 2)
        self.dx = self.ax * (self.DASH_SPEED / hyp)
        self.dy = self.ay * (self.DASH_SPEED / hyp)
        self.is_dashing = True
        self.dash_timer = self.DASH_TIME
