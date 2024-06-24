from .tile import Tile

class StarMap:

    def __init__(self, width = 20, height = 20, map = None):
        self.width = width
        self.height = height
        if (map == None):
            self.map = [[0 for x in range(width)] for y in range(height)] 
        else:
            self.map = map

    def getWidth(self):
        return self.width
    
    def getHeight(self):
        return self.height

    def getTile(self, x, y):
        if (x < 0 or x >= self.width):
            return Tile()

        if (y < 0 or y >= self.width):
            return Tile()
        
        if (self.map[y][x] == 0):
            return Tile(val = self.map[y][x], passable = True)
        else:
            return Tile(val = self.map[y][x], passable = False)

    def setTile(self, tile, x, y):
        self.map[y][x] = tile

    def testMap():
        map = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 1, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        return StarMap(10, 10, map)