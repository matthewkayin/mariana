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

        # Initialize the map
        self.map = map.Map()
        self.map.load_mapfile("data/map/frens.map")

        # Initialize the camera
        self.CAMERA_RIGHT = 1280 * 0.75
        self.CAMERA_LEFT = 1280 * 0.25
        self.CAMERA_TOP = 720 * 0.25
        self.CAMERA_BOT = 720 * 0.75
        self.camera_x = 0
        self.camera_y = 0

        # Set camera position based on player spawn in map
        self.spawn_player_at_tile(self.map.player_spawn)

    def spawn_player_at_tile(self, pos):
        """
        This spawns the player in the center of the tile at the given tile coordinate
        """

        # Get x and y variables from the pos
        x = pos[0]
        y = pos[1]

        # Set the player in teh correct tile
        self.player.x = x * self.map.TILE_WIDTH
        self.player.y = y * self.map.TILE_HEIGHT

        # Center the player position within that tile
        x_diff = self.map.TILE_WIDTH - self.player.w
        y_diff = self.map.TILE_HEIGHT - self.player.h
        x_offset = int(x_diff / 2)
        y_offset = int(y_diff / 2)
        self.player.x += x_offset
        self.player.y += y_offset

        # Now set the camera according to player pos
        # TODO test to make sure that the camera doesn't break at any point by us doing this
        self.camera_x = self.player.x - (1280 / 2)
        self.camera_y = self.player.y - (720 / 2)

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

    def get_collider_rect(self, collider):
        x = (collider[0] * self.map.TILE_WIDTH) - self.camera_x
        y = (collider[1] * self.map.TILE_HEIGHT) - self.camera_y
        w = 64
        h = 64
        return pygame.Rect(x, y, w, h)

    def update(self, delta, input_queue, input_states):
        """
        Updates the level logic
        """

        # First update the player
        self.update_player(delta, input_queue, input_states)

        # Check player collisions
        self.check_collisions(delta)

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

    def check_collisions(self, delta):
        """
        Checks and handles game collisions
        """
        player_rect = self.get_rect(self.player)
        wall_collision_occured = False
        for collider in self.map.colliders:
            if player_rect.colliderect(self.get_collider_rect(collider)):
                # We have a collision, so let's first revert player to pre-collision coords
                x_step = self.player.dx * delta
                y_step = self.player.dy * delta
                self.player.x -= x_step
                self.player.y -= y_step

                # Now check if collision is caused by x dir or y dir movement
                self.player.x += x_step  # x dir move check
                player_rect = self.get_rect(self.player)
                x_causes_collision = player_rect.colliderect(self.get_collider_rect(collider))
                self.player.x -= x_step

                self.player.y += y_step  # y dir move check
                player_rect = self.get_rect(self.player)
                y_causes_collision = player_rect.colliderect(self.get_collider_rect(collider))
                self.player.y -= y_step

                # If x movement doesn't cause collision, go ahead and keep doing x movement
                if not x_causes_collision:
                    self.player.x += x_step
                # else:
                #    self.player.dx = 0

                # Same with y dir movement
                if not y_causes_collision:
                    self.player.y += y_step
                # else:
                #    self.player.dy = 0

                self.player.handle_collision()
                wall_collision_occured = True
                player_rect = self.get_rect(self.player)
        if not wall_collision_occured:
            self.player.on_wall = False

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
        #
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
