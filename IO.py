import json
import os
import shutil
import urllib2
import sys

from flask import Flask
from setuptools.command.setopt import config_file


__authors__ = 'posix88 & Otacon'
__license__ = "GNU GPL v3.0"
from os.path import expanduser
from os import path


class HTTPDownload(object):
    def __init__(self, url, callback=None, local_file=None):
        """
        :type url: str
        :type callback: func
        :type local_file: str
        """
        self._url = url
        self._size = 0
        self._callback = callback
        self._file = local_file
        if not self._url is None and not file is None:
            self._file = self._url.split('/')[-1]

    @property
    def url(self):
        return self._url

    @property
    def size(self):
        return self._size

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, local_file):
        self._file = local_file

    def set_progress_callback(self, callback):
        self._callback = callback

    def start(self, path_download):
        destination_file = path.join(path_download, self._file)
        if path.exists(destination_file):
            print("File exists. Skipping.")
            return
        response = urllib2.urlopen(self._url)
        destination = open(destination_file, 'wb')
        meta = response.info()
        total = int(meta.getheaders("Content-Length")[0])
        downloaded = 0
        buff_size = 1024
        print("Downloading: {0} ({1}KB)".format(self._file, repr(total / 1024)))
        while True:
            buff = response.read(buff_size)

            if not buff:
                break

            downloaded += len(buff)
            destination.write(buff)
            if self._callback:
                self._callback(downloaded, total)

        destination.close()
        print("\nDownload completed")


class PublicIpGetter(object):
    @property
    def ip(self):
        return "127.0.0.1"


class HttpBin(PublicIpGetter):
    @property
    def ip(self):
        response = urllib2.urlopen("http://httpbin.org/ip")
        ip = json.load(response)
        return ip['origin']


class FileSystem(object):
    def __init__(self, home=expanduser("~")):
        """
        :type home: str
        """
        self._root = path.join(home, ".mineserver")
        self._bins = path.join(self._root, "bins")
        self._servers = path.join(self._root, "servers")

        if not path.exists(self._root):
            print("Creating folder {0}".format(self._root))
            os.mkdir(self._root)
        if not path.exists(self._bins):
            print("Creating folder {0}".format(self._bins))
            os.mkdir(self._bins)
        if not path.exists(self._servers):
            print("Creating folder {0}".format(self._servers))
            os.mkdir(self._servers)

    @property
    def bins(self):
        """
        :rtype: str
        """
        return self._bins

    @property
    def servers(self):
        """
        :rtype: str
        """
        return self._servers


class ServerProperty(object):
    def __init__(self, name, type, default, description, value):
        self._name = name
        self._type = type
        self._default = default
        self._description = description
        if (value != None):
            self._value = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, default):
        self._default = default

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class ServerMaker(object):
    def __init__(self, file_system=FileSystem(), name="server"):
        """
        :type file_system: FileSystem
        :type name: str
        """
        self._file_system = file_system
        self._name = name

    def config(self):
        download = HTTPDownload("https://s3.amazonaws.com/Minecraft.Download/versions/1.8/minecraft_server.1.8.jar")
        source = path.join(self._file_system.bins, download.file)
        destination = path.join(self._file_system.servers, self._name)
        if not self.__check_destination(download, destination):
            self.__start_download(download, self._file_system.bins)
            self.__copy_to_destination(source, destination)

    @property
    def file_system(self):
        '''
        :rtype: FileSystem
        '''

        return self._file_system

    @property
    def name(self):
        '''
        :rtype: str
        '''
        return self._name

    @property
    def server_path(self):
        '''
        :rtype string
        '''
        return os.path.join(self._file_system.servers,self._name)

    @staticmethod
    def __check_destination(download, new_path):
        destination = path.join(new_path, download.file)
        return path.exists(destination)

    @staticmethod
    def __start_download(download, bins):
        listener = lambda down, total: sys.stdout.write(
            "\rDownloaded {0}KB/{1}KB".format(repr(down / 1024), repr(total / 1024)))
        download.set_progress_callback(listener)
        download.start(bins)

    @staticmethod
    def __copy_to_destination(source, destination):
        if not path.exists(destination):
            print("Creating folder {0}".format(source))
            os.mkdir(destination)
        print("Copying {0} to {1} ...".format(source, destination))
        shutil.copy(source, destination)

    def setup_folder(self):
        properties = "server.properties"
        propertiesPath = os.path.join(self._file_system.bins, properties)
        self.config()
        if not os.path.isfile(propertiesPath):
            file = open(propertiesPath, "w")
            file.close()
            # self._create_sp() TODO aggiungere argomenti che ci ispirano
            # l'eula credo bisogna scaricarla

    def _create_sp(self, startup_values={}):
        # Popolamento del Server.properties
        serverProperty = ServerProperty('server-port', int, 25565, 'Server Port', None)
        defaults = {
            'server-port': 25565,
            'max-players': 20,
            'level-seed': '',
            'gamemode': 0,
            'difficulty': 1,
            'level-type': 'DEFAULT',
            'level-name': 'world',
            'max-build-height': 256,
            'generate-structures': 'true',
            'generator-settings': '',
            'server-ip': '0.0.0.0',
            'enable-rcon': 'true',
            'motd': 'Welcome to Mordor!',
        }

        for option, value in startup_values.iteritems():
            defaults[option] = value

            # DA CONTROLLARE SE FUNZIONA
        with config_file(os.path.join(self._file_system.bins, "server.properties")) as sp:
            sp.use_sections(False)
            for key, value in defaults.iteritems():
                sp[key] = str(value)


def test_http_server():
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Hello World!'

    @property
    @app.route('/api/servers/')
    def servers():
        fs = FileSystem()
        dirs = os.listdir(fs.servers)

        servs = []
        for serv in dirs:
            servs.append(serv)

        return json.dumps(servs)

    @property
    @app.route('/api/servers/<server>')
    def server(server):
        reply = {"name": server}
        fs = FileSystem()
        server_path = os.path.join(fs.servers, server)
        if path.exists(server_path):
            reply["exists"] = True

        contains_properties = False
        contains_jar = False
        for item in os.listdir(server_path):
            if not contains_properties:
                contains_properties = ".properties" in item
            if not contains_jar:
                contains_jar = ".jar" in item

        reply["jar"] = contains_jar
        reply["properties"] = contains_properties
        return json.dumps(reply)


    app.run(debug=True)


def test_server_maker():
    server_maker = ServerMaker()
    server_maker.config()
    print("Server created.")


def test_public_ip():
    ip = HttpBin().ip
    print(ip)


def test_http_download(download_path):
    download = HTTPDownload("https://s3.amazonaws.com/Minecraft.Download/versions/1.8/minecraft_server.1.8.jar")
    listener = lambda down, total: sys.stdout.write(
        "\rDownloaded {0}kb out of {1}kb".format(repr(down / 1024), repr(total / 1024)))
    download.set_progress_callback(listener)
    download.start(download_path)

