import unittest

from star_map import StarMap

class StarMapTest(unittest.TestCase):

    def test_size(self):
        s = StarMap(20, 30)
        self.assertTrue(20, s.getWidth())
        self.assertTrue(30, s.getHeight())


if __name__ == '__main__':
    unittest.main()