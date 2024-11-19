import unittest

from direction_coordinator import DirectionCoordinator
from general.star_map import StarMap

class DirectionCoordinatorTest(unittest.TestCase):

    def test_4_cards_4_allowed_returns_the_same_directions_always(self):
        d = DirectionCoordinator("1234")
        self.assertEqual("1234", d.get_next_direction_cards())
        d.move("1")
        self.assertEqual("1234", d.get_next_direction_cards())
        d.move("2")
        self.assertEqual("1234", d.get_next_direction_cards())
        d.move("3")
        self.assertEqual("1234", d.get_next_direction_cards())
        d.move("4")
        self.assertEqual("1234", d.get_next_direction_cards())

    def test_4_cards_1_allowed_returns_the_next_card_and_loops(self):
        d = DirectionCoordinator("1234", 1)
        self.assertEqual("1", d.get_next_direction_cards())
        d.move("1")
        self.assertEqual("2", d.get_next_direction_cards())
        d.move("2")
        self.assertEqual("3", d.get_next_direction_cards())
        d.move("3")
        d.curY = 15 # need to relocate spaceship so we don't cross movement path
        self.assertEqual("4", d.get_next_direction_cards())
        d.move("4")
        self.assertEqual("1", d.get_next_direction_cards())

    def test_4_cards_3_allowed_loops_correctly(self):
        d = DirectionCoordinator("1234", 3)
        self.assertEqual("123", d.get_next_direction_cards())
        d.move("1")
        self.assertEqual("412", d.get_next_direction_cards())
        d.move("1")
        self.assertEqual("341", d.get_next_direction_cards())
        d.move("1")
        self.assertEqual("234", d.get_next_direction_cards())
        d.move("1")
        self.assertEqual("234", d.get_next_direction_cards())  # Would be 123, but the move was not legal.


    def test_all_directions_possible_to_start(self):
        d = DirectionCoordinator("1234")
        self.assertEqual('1234', d.get_possible_directions())

    def test_opposite_of_last_direction_is_invalid(self):
        d = DirectionCoordinator("1234")
        d.move("1")
        self.assertEqual('124', d.get_possible_directions())
        d.move("2")
        self.assertEqual('123', d.get_possible_directions())
        d.move("3")
        self.assertEqual('23', d.get_possible_directions()) # Can't go left because already travelled
        d.move("3")
        self.assertEqual('234', d.get_possible_directions())
        d.move("4")
        self.assertEqual('34', d.get_possible_directions()) # Can't go up because already travelled


    def test_opposite_of_last_direction_is_invalid_with_3_cards_allowed(self):
        d = DirectionCoordinator("1234", 3)
        self.assertEqual('123', d.get_possible_directions())  # Only the first 3 are allowed choices.
        d.move("1")
        self.assertEqual('412', d.get_possible_directions()) 
        d.move("1")
        self.assertEqual('41', d.get_possible_directions()) # Next 3 cards would be 341, but 3 is illegal (opposite of 1)
        d.move("4")
        self.assertEqual('34', d.get_possible_directions()) # Next 3 cards would be 234, but 2 is illegal (opposite of 4)
        d.move("3")
        self.assertEqual('3', d.get_possible_directions()) # Next 3 cards would be 123, but 1 is illegal (opposite of 3), 2 is illegal because already travelled
        d.move("3")
        self.assertEqual('4', d.get_possible_directions()) # Next 3 cards would be 412, but 1 is illegal (opposite of 4), 2 is illegal because already travelled

    def test_map_boundaries_are_respected(self):
        d = DirectionCoordinator("1234", max_direction_cards = 4, curX = 2, curY = 2, map = StarMap(width = 10, height = 10))
        self.assertEqual('1234', d.get_possible_directions())
        d.move("1") 
        self.assertEqual(1, d.getCurY())
        self.assertEqual('124', d.get_possible_directions()) # 3 illegal because opposite direction
        d.move("1") 
        self.assertEqual(0, d.getCurY())
        self.assertEqual('24', d.get_possible_directions()) # 3 illegal because opposite direction, 1 illegal because of map boundary
        d.move("4") 
        self.assertEqual(1, d.getCurX())
        self.assertEqual('34', d.get_possible_directions()) # Can't go up, already there
        d.move("4") 
        self.assertEqual(0, d.getCurX())
        self.assertEqual('3', d.get_possible_directions()) # Top left corner, coming from 2
        
        for i in range(0, 8):
            d.move("3")
            self.assertEqual(0, d.getCurX())
            self.assertEqual('23', d.get_possible_directions()) # Can't go left, at the boundary
    
        d.move("3")
        self.assertEqual(0, d.getCurX())
        self.assertEqual(9, d.getCurY())    
        self.assertEqual('2', d.get_possible_directions()) # Bottom left corner
        
        for i in range(0, 8):
            d.move("2")
            self.assertEqual(9, d.getCurY())
            self.assertEqual('12', d.get_possible_directions()) # Can't go down
        
        d.move("2")
        self.assertEqual(9, d.getCurX())
        self.assertEqual(9, d.getCurY())    
        self.assertEqual('1', d.get_possible_directions()) # Bottom right corner

        for i in range(0, 8):
            d.move("1")
            self.assertEqual(9, d.getCurX())
            self.assertEqual('14', d.get_possible_directions()) # Can't go right
        
        d.move("1")
        self.assertEqual(9, d.getCurX())
        self.assertEqual(0, d.getCurY())    
        self.assertEqual('4', d.get_possible_directions()) # top right corner
        
        for i in range(0, 5):
            d.move("4")
            self.assertEqual(0, d.getCurY())
            self.assertEqual('34', d.get_possible_directions()) # Can't go up
        
        d.move("4")
        self.assertEqual('3', d.get_possible_directions()) # Can't go up, can't go left because already travelled
    
        
    def test_map_with_stars(self):
        d = DirectionCoordinator("1234", max_direction_cards = 4, curX = 0, curY = 0, map = StarMap.testMap())
        self.assertEqual('23', d.get_possible_directions()) # top left corner
        d.move("2")
        self.assertEqual('2', d.get_possible_directions()) # land direction down
        d.move("2")
        self.assertEqual('23', d.get_possible_directions()) # no land direction down
        d.move("3")
        self.assertEqual('2', d.get_possible_directions()) # land left and down
        d.move("2")
        self.assertEqual('123', d.get_possible_directions()) # no land
        d.move("3")
        self.assertEqual('2', d.get_possible_directions()) 
    
        d = DirectionCoordinator("1234", max_direction_cards = 4, curX = 0, curY = 4, map = StarMap.testMap())
        self.assertEqual('123', d.get_possible_directions()) 
        d.move("2")
        self.assertEqual('', d.get_possible_directions()) 
        
        d = DirectionCoordinator("1234", max_direction_cards = 4, curX = 3, curY = 4, map = StarMap.testMap())
        self.assertEqual('', d.get_possible_directions()) 
    
    def test_cannot_cross_line(self):
        d = DirectionCoordinator("1234", max_direction_cards = 4, curX = 2, curY = 2, map = StarMap(width = 10, height = 10))
        d.move("2")
        self.assertEqual('123', d.get_possible_directions()) 
        d.move("2")
        self.assertEqual('123', d.get_possible_directions())
        d.move("3")
        self.assertEqual('234', d.get_possible_directions())
        d.move("4")
        self.assertEqual('34', d.get_possible_directions()) # Can't go up, because was there already

    def test_can_cross_line_after_repair(self):
        d = DirectionCoordinator("1234", max_direction_cards = 4, curX = 2, curY = 2, map = StarMap(width = 10, height = 10))
        d.move("2")
        self.assertEqual('123', d.get_possible_directions()) 
        d.move("2")
        self.assertEqual('123', d.get_possible_directions())
        d.move("3")
        self.assertEqual('234', d.get_possible_directions())
        d.move("4")
        d.repair_complete()
        self.assertEqual('134', d.get_possible_directions()) # Can't go up, because was there already

    def test_prevent_moving_into_things(self):
        d = DirectionCoordinator("1234", max_direction_cards = 4, curX = 2, curY = 2, map = StarMap(width = 10, height = 10))
        self.assertEqual(True, d.move("2"))
        self.assertEqual('123', d.get_possible_directions()) 
        self.assertEqual(False, d.move("4"))  # Tried to move backwards

if __name__ == '__main__':
    unittest.main()