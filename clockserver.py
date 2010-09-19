#!/usr/bin/python
# vim:fileencoding=utf8

from SimpleXMLRPCServer import SimpleXMLRPCServer
from datetime import datetime
from ConfigParser import SafeConfigParser
import sys, subprocess
import os

class AlarmClock(object):
    def __init__(self, config):
        self.enabled = config.getboolean('alarm', 'enabled')
        time = config.get('alarm', 'time')
        (self.hour, self.minute) = [int(i) for i in time.split(":")]
        self.command = config.get('alarm', 'command')
        self.config = config

    def tick(self):
        if not self.enabled: return
        now = datetime.now()
        if (self.hour, self.minute) == (now.hour, now.minute):
            self.enabled = False
            self.execute()
            self.update_config()

    def execute(self):
       subprocess.call(self.command, shell=True) 

    def update_config(self):
        self.config.set('alarm', 'enabled', str(self.enabled))
        self.config.set('alarm', 'time', "%s:%s" % (self.hour, self.minute))
        self.config.write(open("alarmclock.conf", "w"))

    def _dispatch(self, method, params):
        self.tick()
        if method == "set":
            (self.hour, self.minute) = params
        elif method == "time":
            return (self.hour, self.minute)
        elif method == "enable":
            self.enabled = params[0]
        elif method == "enabled":
            return self.enabled
        else:
            raise AttributeError
        self.tick()
        self.update_config()
        return "OK"

class Server(SimpleXMLRPCServer):
    timeout = 20
    def handle_timeout(self):
        self.instance.tick()

server = Server(("localhost", 8000), logRequests = False)

now = datetime.now()

config = SafeConfigParser()
config.read('alarmclock.conf')

a = AlarmClock(config)

server.register_instance(a)

print "Daemonizing..."

pid = os.fork()
if pid:
    print "Forked to pid %d" % pid
    sys.exit(0)


while True:
    server.handle_request()
