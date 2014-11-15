import random
from unittest import TestCase
from Common import Position


__author__ = 'Orfeo'


class TestInitPosition(TestCase):
    def setUp(self):
        self._position = Position()

    def test_x(self):
        self.assertEqual(self._position.x, 0)

    def test_y(self):
        self.assertEqual(self._position.y, 0)

    def test_z(self):
        self.assertEqual(self._position.z, 0)


class TestRandomPosition(TestCase):
    def setUp(self):
        self._x = random.randint(0, 100)
        self._y = random.randint(0, 100)
        self._z = random.randint(0, 100)
        self._position = Position(self._x, self._y, self._z)

    def test_x(self):
        self.assertEqual(self._position.x, self._x)

    def test_y(self):
        self.assertEqual(self._position.y, self._y)

    def test_z(self):
        self.assertEqual(self._position.z, self._z)
