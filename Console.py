from distutils.spawn import find_executable
import json
import socket
import struct
import re
from abc import ABCMeta, abstractmethod

from Common import Player


__authors__ = 'posix88 & Otacon'
__license__ = "GNU GPL v3.0"


class Process(object):
    def __init__(self, name):
        """
        :type name: str
        """
        self._pid = -1
        self._name = find_executable(name)

    @property
    def pid(self):
        """
        :rtype: int
        """
        return self._pid

    @pid.setter
    def pid(self, pid):
        """
        :type pid: int
        :return: None
        """
        self._pid = pid

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        :type name: str
        :rtype: None
        """
        self._name = find_executable(name)
        if self.name is None:
            raise IOError("Executable %s not found" % self.name)

    def run(self):
        self._pid = None
        raise NotImplementedError


class Command(object):
    def __init__(self, cmd, args=None):
        """
        :type cmd: str
        :type args: list[str]
        :rtype:
        """
        self._cmd = cmd
        self._args = args

    @property
    def command(self):
        """
        :rtype: str
        """
        return self._cmd

    @command.setter
    def command(self, cmd):
        """
        :type cmd: str
        """
        cmd = cmd.strip()
        if cmd.startswith('/'):
            self._cmd = cmd
        else:
            self._cmd = '/' + cmd

    @property
    def args(self):
        """
        :rtype: list[str]
        """
        return self._args

    @args.setter
    def args(self, args):
        """
        :type args: list[str]
        """
        self._args = args


class MinecraftShell(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def attach(self):
        pass

    @abstractmethod
    def detach(self):
        pass

    @abstractmethod
    def execute(self, command):
        pass

    def spawn_point(self, player=None, pos=None):
        command = "spawnpoint"
        if player:
            command = command + " " + player.name
        if pos:
            command = command + " " + repr(pos.x) + " " + repr(pos.y) + " " + repr(pos.z)

    def set_world_spawn(self, pos=None):
        command = "setworldspawn"
        if (pos):
            command = command + " " + repr(pos.x) + " " + repr(pos.y) + " " + repr(pos.z)
        self.execute(command)

    def enable_auto_saving(self, save=True):
        if (save):
            self.execute("save-on")
        else:
            self.execute("save-off")

    def save(self):
        self.execute("save-all")

    def ban(self, players, reason=""):
        if type(players) is list:
            for player in players:
                self.execute("ban " + player.name + " " + reason)
        else:
            self.execute("ban " + players.name + " " + reason)

    def op(self, players):
        if type(players) is list:
            for player in players:
                self.execute("op " + player.name)
        else:
            self.execute("op " + players.name)

    def say(self, text, player="@a", bold=False, italic=False, underlined=False, strikethrough=False,
            obfuscated=False, color="reset"):
        js = {'text': "[Sauron] - ", 'bold': True, 'underline': True, 'color': "red"}
        extra = {'text': text, 'bold': bold, 'italic': italic, 'underlined': underlined, 'strikethrough': strikethrough,
                 'obfuscated': obfuscated, 'color': color}
        js["extra"] = [extra]
        message = json.dumps(js)
        return self.execute("tellraw " + player + " " + message)

    def list(self):
        self.execute("list")

    def kick(self, players, reason=""):
        if type(players) is list:
            for player in players:
                self.execute("kick " + player.name + " " + reason)
        else:
            self.execute("kick " + players.name + " " + reason)

    def kickAll(self, reason=""):
        players = self.list()
        self.kick(players, reason)


class RCon(MinecraftShell):
    class Message(object):

        class Type():
            RESPONSE = 0
            COMMAND = 2
            LOGIN = 3

        def __init__(self, data="", comm_type=Type.COMMAND, seq=0):
            self._data = data
            self._type = comm_type
            self._seq = seq
            self._length = 10 + len(data)

        @property
        def type(self):
            return self._type

        @type.setter
        def type(self, cmd_type):
            self_type = cmd_type

        @property
        def data(self):
            return self._data

        @data.setter
        def data(self, data):
            self._length = 10 + len(data)
            self._data = data

        @property
        def length(self):
            return self._length

        @length.setter
        def length(self, length):
            self._length = length

        @property
        def sequence(self):
            return self._seq

        @sequence.setter
        def sequence(self, seq=0):
            self._seq = seq

        @property
        def binary(self):
            return struct.pack('<iii', self._length, self._seq, self._type) + self._data + "\x00\x00"

        def __repr__(self):
            return 'len=' + repr(self._length) + ', seq=' + repr(self._seq) + ', type=' + repr(
                self._type) + ', data=' + self._data

    def __init__(self, password, port=25575, host="localhost", debug=False):
        self._port = port
        self._host = host
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(10)
        self._debug = debug
        self._password = password

    def _send(self, command):
        if self._debug:
            print( "> " + repr(command))
        self._sock.send(command.binary)
        reply = self._receive()
        if self._debug:
            print("< " + repr(reply))
        return reply

    def _receive(self):
        data = self._sock.recv(12)
        message = RCon.Message()
        req_length, req_seq, req_type = struct.unpack('<iii', data)
        response = self._sock.recv(req_length - 8)
        if response[-2:] != '\x00\x00':
            raise Exception("No final padding in message")

        message.length = req_length
        message.type = req_type
        message.sequence = req_seq
        message.data = response[:-2]
        return message

    def _connect(self):
        self._sock.connect((self._host, self._port))
        if self._debug:
            print("Connecting to " + self._host + ":" + repr(self._port) + " ...")

    def _auth(self):
        if self._debug:
            print("Authenticating with password: " + self._password)
        message = RCon.Message(self._password, RCon.Message.Type.LOGIN)
        reply = self._send(message)
        if reply.sequence >= 0:
            if self._debug:
                print("Authenticated.")
            return True
        else:
            raise Exception("Authentication failed with password \"" + self._password + "\"")

    def attach(self):
        self._connect()
        self._auth()

    def list(self):
        reply = self.execute("list")
        p = re.compile(ur'^There are ([0-9]*)\/[0-9]* players online:((?:\s?\w*)*)')
        groups = re.match(p, reply)
        count = int(groups.group(1))
        if count <= 0:
            return []
        else:
            player_list = []
            name_list = groups.group(2).split()
            for name in name_list:
                player_list.append(Player(name))

        return player_list

    def execute(self, command=""):
        command = RCon.Message(command, RCon.Message.Type.COMMAND)
        reply = self._send(command)
        if reply.sequence >= 0:
            if reply.data.startswith("Unknown command"):
                raise Exception('Invalid Command "' + command.data + '"')
            else:
                return reply.data
        else:
            raise Exception("Unauthorized")

    def detach(self):
        if self._debug:
            print("Disconnected.")
        self._sock.close()


def test_rcon():
    try:
        shell = RCon("orfeo", debug=True)
        shell.attach()
        shell.say("ciao")
        # testing
        if False:
            players = shell.list()
            shell.kick(players)
        else:
            shell.kickAll()
        # sending invalid command, sequence is not respected by protocol
        shell.execute("bau")
    except Exception as e:
        print("Error: " + str(e))
    finally:
        shell.detach()


def test_minecraft():
    minecraft = MinecraftShell("vanilla180")
    comm = Command("list")
    result = minecraft.execute(comm)
    result_raw = minecraft.execute_raw_command("/list")


if __name__ == "__main__":
    test_rcon()
    # test_http_server()
    # test_server_maker()
    # test_setup_folder()
    # test_public_ip()
    # test_http_download()
    # test_player()
    # test_minecraft()



