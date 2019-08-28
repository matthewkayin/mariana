# Mariana
# Code - Matt Madden
# map.py -- This has the map class

import os
import sys


class Map():
    def __init__(self):
        """
        The tile variable contains indices of each floor tile
        So _tile[x][y] = i where i is the value of that tile
        Then each index i has a corresponding tile name in _tile_map
        """
        self._tiles = []
        self._walls = []

        self.WIDTH_IN_TILES = 0
        self.HEIGHT_IN_TILES = 0
        self.START_X = 0
        self.START_Y = 0

        self.TILE_WIDTH = 64
        self.TILE_HEIGHT = 64

        self.MAX_CAMERA_X = 0
        self.MIN_CAMERA_X = 0
        self.MAX_CAMERA_Y = 0
        self.MIN_CAMERA_Y = 0

        self.MAX_ENTITY_X = 0
        self.MIN_ENTITY_X = 0
        self.MAX_ENTITY_Y = 0
        self.MIN_ENTITY_Y = 0

        self.tileset = ""
        self.alphas = []

    def load_mapfile(self, filename):
        """
        Takes a tet file and reads the map in from in
        """

        # First check if file exists
        if not os.path.isfile(filename):
            print("Error! Could not find " + filename)
            sys.exit(0)

        # Now read the file
        map_file = open(filename, "r")
        mode = ""
        floor_data = []
        wall_data = []
        special_data = []
        for line in map_file.read().splitlines():
            if line.startswith("tileset="):
                self.tileset = line[(line.index("=") + 1):]
            elif line.startswith("alpha-tileset="):
                self.alpha_tileset = line[(line.index("=") + 1):]
            elif line.startswith("width="):
                self.WIDTH_IN_TILES = int(line[(line.index("=") + 1):])
            elif line.startswith("height="):
                self.HEIGHT_IN_TILES = int(line[(line.index("=") + 1):])
            elif line.startswith("layer="):
                mode = line[(line.index("=") + 1):]
            else:
                if mode == "floor":
                    floor_data.append(line.split(","))
                elif mode == "wall":
                    wall_data.append(line.split(","))
                elif mode == "special":
                    special_data.append(line.split(","))
        map_file.close()

        # Since we have the tilset now is a good time to load in the tileset metadata and to verify that the tileset exists
        if not os.path.isfile("res/gfx/" + self.tileset + ".png"):
            print("Error! Tileset res/gfx/" + self.tileset + ".png not found!")
            sys.exit(0)
        if not os.path.isfile("res/gfx/" + self.tileset + ".txt"):
            print("Error! Tileset metadata file res/gfx/" + self.tileset + ".txt not found!")
            sys.exit(0)

        meta_file = open("res/gfx/" + self.tileset + ".txt")
        for line in meta_file.read().splitlines():
            if line.startswith("alphas="):
                alphas_as_string = line[(line.index("=") + 1):]
                self.alphas = list(map(int, alphas_as_string.split(",")))
                for i in range(0, len(self.alphas)):
                    self.alphas[i] -= 1
        meta_file.close()

        # Now setup the tiles with the appropriate dimensions
        self._tiles = []
        self._walls = []
        for x in range(0, self.WIDTH_IN_TILES):
            self._tiles.append([])
            self._walls.append([])
            for y in range(0, self.HEIGHT_IN_TILES):
                self._tiles[x].append(0)
                self._walls[x].append(0)

        # And copy the map data to the tiles values
        for x in range(0, self.WIDTH_IN_TILES):
            for y in range(0, self.HEIGHT_IN_TILES):
                self._tiles[x][y] = int(floor_data[y][x]) - 1
                self._walls[x][y] = int(wall_data[y][x]) - 1

        self.MAX_CAMERA_X = self.get_width() - 1280
        self.MIN_CAMERA_X = 0
        self.MAX_CAMERA_Y = self.get_height() - 720
        self.MIN_CAMERA_Y = 0

        self.MAX_ENTITY_X = self.get_width()
        self.MIN_ENTITY_X = 0
        self.MAX_ENTITY_Y = self.get_height()
        self.MIN_ENTITY_Y = 0

    def get_tile(self, x, y):
        """
        Return the image id of the tile at the x and y coords
        """

        return self._tiles[x][y]

    def get_wall(self, x, y):
        """
        Return the image id of the tile at the x and y coords on the wall layer
        Returns -1 if there is no wall there
        """

        # Note, it returns -1 because of the way data is read in in load_mapfile()
        return self._walls[x][y]

    def get_width(self):
        """
        Returns the width in pixels of the map
        """
        return self.WIDTH_IN_TILES * self.TILE_WIDTH

    def get_height(self):
        """
        Returns the height in pixels of the map
        """
        return self.HEIGHT_IN_TILES * self.TILE_HEIGHT
