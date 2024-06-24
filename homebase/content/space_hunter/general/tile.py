
class Tile:
    def __init__(self, val = 0, passable = True):
        self.val = val
        self.passable = passable

    def notPassable(self):
        return not self.isPassable()
    
    def isPassable(self):
        return self.passable