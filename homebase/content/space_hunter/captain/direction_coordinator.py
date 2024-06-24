import sys
sys.path.append('../')

from general.star_map import StarMap
from general.tile import Tile

class DirectionCoordinator:
    last_direction = "0"
    allowed_direction_cards = 4
    last_direction_card = 0
    opposite_directions = {
        "0": "",
        "1": "3",
        "2": "4",
        "3": "1",
        "4": "2"
    }

    def __init__(self, direction_cards, max_direction_cards = 4, curX = 10, curY = 10, map = StarMap()):
        self.direction_cards = direction_cards
        self.max_direction_cards = max_direction_cards
        self.allowed_direction_cards = max_direction_cards
        self.curX = curX
        self.curY = curY
        self.map = map
        self.movement_map = StarMap(width = map.getWidth(), height = map.getHeight())

    def get_next_direction_cards(self):
        if (self.last_direction_card + self.allowed_direction_cards >= len(self.direction_cards)):
            # Take as many as possible from the end.
            last = self.direction_cards[self.last_direction_card:self.last_direction_card + self.max_direction_cards]
            # Add as many as necessary from the beginning
            return last + self.direction_cards[0:self.allowed_direction_cards-len(last)]
        else:
            return self.direction_cards[self.last_direction_card:self.last_direction_card + self.max_direction_cards]

    def get_possible_directions(self):
        directions = self.get_next_direction_cards()
        possible_directions = self.remove_illegal_directions(directions)
        return possible_directions
  
    def remove_illegal_directions(self, directions):
        directions = directions.replace(self.opposite_directions[self.last_direction], "")  # Remove opposite direction
        
        # Remove when on map boundary
        if (self.curX == 0):
            directions = directions.replace("4", "")
        if (self.curY == 0):
            directions = directions.replace("1", "")
        if (self.curX == self.map.getWidth() - 1):
            directions = directions.replace("2", "")
        if (self.curY == self.map.getHeight() - 1):
            directions = directions.replace("3", "")
        
        # Remove when adjacent to non-passable square
        if (self.map.getTile(self.curX - 1, self.curY).notPassable()):
            directions = directions.replace("4", "")

        if (self.map.getTile(self.curX + 1, self.curY).notPassable()):
            directions = directions.replace("2", "")

        if (self.map.getTile(self.curX, self.curY - 1).notPassable()):
            directions = directions.replace("1", "")

        if (self.map.getTile(self.curX, self.curY + 1).notPassable()):
            directions = directions.replace("3", "")
    
        # Remove if direction would cross the travelled path
        if (self.movement_map.getTile(self.curX - 1, self.curY).notPassable()):
            directions = directions.replace("4", "")

        if (self.movement_map.getTile(self.curX + 1, self.curY).notPassable()):
            directions = directions.replace("2", "")

        if (self.movement_map.getTile(self.curX, self.curY - 1).notPassable()):
            directions = directions.replace("1", "")

        if (self.movement_map.getTile(self.curX, self.curY + 1).notPassable()):
            directions = directions.replace("3", "")
        
        return directions

    def move(self, direction):
        self.last_direction = direction

        # Before moving, mark the current location as travelled
        self.movement_map.setTile(Tile(val = 1, passable = False), self.curX, self.curY)

        if direction == "1":
            self.curY = self.curY - 1
        if direction == "3":
            self.curY = self.curY + 1
        if direction == "2":
            self.curX = self.curX + 1
        if direction == "4":
            self.curX = self.curX - 1
        
        self.last_direction_card = self.last_direction_card + self.allowed_direction_cards
        if (self.last_direction_card >= len(self.direction_cards)):
            self.last_direction_card = self.last_direction_card - len(self.direction_cards)

    def repair_complete(self):
        # Reset movement map
        self.movement_map = StarMap(width = self.map.getWidth(), height = self.map.getHeight())

    def getCurX(self):
        return self.curX
    
    def getCurY(self):
        return self.curY