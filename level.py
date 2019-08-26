# Mariana
# Code - Matt Madden
# level.py -- Logic for actual gameplay goes here

import entities
import map
import pygame
import math


class Level():
    def __init__(self):
        """
        Default constructor, should only be ran once as the level
        will in the future be able to be given
        """

        # Initialize the player
        self.player = entities.Player()
        # self.player.x += 1280
        # self.player.y += 720

        self.map = map.Map()
        self.map.load_mapfile("frens.map")
        # self.map.load_map(-1280, -720, 20 * 3, 12 * 3)

        # self.camera_x = 1280
        # self.camera_y = 720
        self.CAMERA_RIGHT = 1280 * 0.75
        self.CAMERA_LEFT = 1280 * 0.25
        self.CAMERA_TOP = 720 * 0.25
        self.CAMERA_BOT = 720 * 0.75
        self.camera_x = 0
        self.camera_y = 0

    def get_rect(self, entity):
        """
        Returns a pygame rect of the passed entity, where the x and y are adjusted to account
        for camera position
        """
        return pygame.Rect(entity.x - self.camera_x, entity.y - self.camera_y, entity.w, entity.h)

    def get_tile_rect(self, x, y):
        """
        Returns a pygame rect of the tile at the passed coordinates, where the x and y are adjusted
        to account for camera position
        """
        return pygame.Rect(self.map.START_X + (x * self.map.TILE_WIDTH) - self.camera_x, self.map.START_Y + (y * self.map.TILE_HEIGHT) - self.camera_y, self.map.TILE_WIDTH, self.map.TILE_HEIGHT)

    def update(self, delta, input_queue, input_states):
        """
        Updates the level logic
        """

        # First update the player
        self.update_player(delta, input_queue, input_states)

        # Now update the camera
        player_rect = self.get_rect(self.player)
        if player_rect.x > self.CAMERA_RIGHT:
            self.camera_x += player_rect.x - self.CAMERA_RIGHT
        elif player_rect.x < self.CAMERA_LEFT:
            self.camera_x += player_rect.x - self.CAMERA_LEFT
        if player_rect.y > self.CAMERA_BOT:
            self.camera_y += player_rect.y - self.CAMERA_BOT
        elif player_rect.y < self.CAMERA_TOP:
            self.camera_y += player_rect.y - self.CAMERA_TOP

        # Make sure the camera hasn't overstepped its bounds
        if self.camera_x > self.map.MAX_CAMERA_X:
            self.camera_x = self.map.MAX_CAMERA_X
        elif self.camera_x < self.map.MIN_CAMERA_X:
            self.camera_x = self.map.MIN_CAMERA_X
        if self.camera_y > self.map.MAX_CAMERA_Y:
            self.camera_y = self.map.MAX_CAMERA_Y
        elif self.camera_y < self.map.MIN_CAMERA_Y:
            self.camera_y = self.map.MIN_CAMERA_Y

    def update_player(self, delta, input_queue, input_states):
        """
        Handles just the player updating, used for code organization
        """
        used_player_move_axis = False
        player_dash = False
        player_reset_dash = False
        player_sprint = self.player.is_sprinting

        # Read the input queue
        while len(input_queue) != 0:
            event = input_queue.pop()
            if event == "AxisMoved:Axis Player Horiz" or event == "AxisMoved:Axis Player Vert":
                used_player_move_axis = True
            elif event == "ButtonDown:Fish Dash":
                player_dash = True
            elif event == "ButtonUp:Fish Dash":
                player_reset_dash = True
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

        # If the player released the dash button, enable the dash action
        if player_reset_dash:
            self.player.can_dash = True

        # Update if the player is sprinting as necessary
        self.player.is_sprinting = player_sprint

        self.player.update(delta)
