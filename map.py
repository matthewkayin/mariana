# Mariana
# Code - Matt Madden
# map.py -- This has the map class


class Map():
    def __init__(self):
        """
        The tile variable contains indices of each floor tile
        So _tile[x][y] = i where i is the value of that tile
        Then each index i has a corresponding tile name in _tile_map
        """
        self._tiles = []
        self._tile_map = ["tile"]

        self.WIDTH_IN_TILES = 0
        self.HEIGHT_IN_TILES = 0
        self.START_X = 0
        self.START_Y = 0

        self.TILE_WIDTH = 64
        self.TILE_HEIGHT = 64

    def load_map(self, start_x, start_y, tile_width, tile_height):
        """
        This function just loads a blank map of the parameter dimensions
        """
        self.START_X = start_x
        self.START_Y = start_y
        self.WIDTH_IN_TILES = tile_width
        self.HEIGHT_IN_TILES = tile_height
        self._tiles = []
        for x in range(0, tile_width):
            self._tiles.append([])
            for y in range(0, tile_height):
                self._tiles[x].append(0)

    def get_tile(self, x, y):
        """
        Return the image name of the tile at the x and y coords
        """
        return self._tile_map[self._tiles[x][y]]

    def get_width(self):
        return self.WIDTH_IN_TILES * self.TILE_WIDTH

    def get_height(self):
        return self.HEIGHT_IN_TILES * self.TILE_HEIGHT
