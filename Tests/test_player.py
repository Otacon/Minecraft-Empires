import random
from unittest import TestCase
from Common import Player, Position

__author__ = 'Orfeo'


class TestInitPlayer(TestCase):

    def setUp(self):
        self._player = Player()

    def test_position(self):
        self.assertEqual(self._player.position.x, 0)
        self.assertEqual(self._player.position.y, 0)
        self.assertEqual(self._player.position.z, 0)

    def test_name(self):
        self.assertIsNone(self._player.name)

class TestCostructorNamePlayer(TestCase):

    def setUp(self):
        self._player = Player("dummy")

    def test_position(self):
        self.assertEqual(self._player.position.x, 0)
        self.assertEqual(self._player.position.y, 0)
        self.assertEqual(self._player.position.z, 0)

    def test_name(self):
        self.assertEquals(self._player.name,"dummy")

class TestCostructorPositionPlayer(TestCase):

    def setUp(self):
        self._x = random.randint(0, 100)
        self._y = random.randint(0, 100)
        self._z = random.randint(0, 100)
        self._player = Player(position=Position(self._x, self._y, self._z))

    def test_position(self):
        self.assertEqual(self._player.position.x, self._x)
        self.assertEqual(self._player.position.y, self._y)
        self.assertEqual(self._player.position.z, self._z)

    def test_name(self):
        self.assertIsNone(self._player.name)