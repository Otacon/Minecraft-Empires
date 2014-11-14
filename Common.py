__authors__ = 'posix88 & Otacon'
__license__ = "GNU GPL v3.0"


class Position(object):
    def __init__(self, x=0, y=0, z=0):
        """
        :rtype : Position
        :type x: int
        :type y: int
        :type z: int
        """

        self._x = x
        self._y = y
        self._z = z

    @property
    def x(self):
        """
        :rtype: int
        """
        return self._x

    @x.setter
    def x(self, x=0):
        """
        :type x: int
        :rtype: None
        """
        self._x = x

    @property
    def y(self):
        """
        :rtype: int
        """
        return self._y

    @y.setter
    def y(self, y=0):
        """
        :type y: int
        :rtype: None
        """
        self._y = y

    @property
    def z(self):
        """
        :rtype: int
        """
        return self._z

    @z.setter
    def z(self, z=0):
        """
        :type z: int
        :rtype: None
        """
        self._z = z


class Player(object):
    def __init__(self, name=None, position=Position()):
        """
        :type name: str
        :type position: Position
        """
        self._name = name
        self._position = position

    @property
    def position(self):
        """
        :rtype: Position
        """
        return self._position

    @position.setter
    def position(self, position):
        """
        :type position: Position
        :rtype : None
        """
        self._position = position

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        """
        :type name: str
        """
        self._name = name

    def __repr__(self):
        return self._name


def test_player():
    play = Player("Orfeo", Position(0, 0, 0))
    play.position = Position(0, 0, 0)
    pos = Position()