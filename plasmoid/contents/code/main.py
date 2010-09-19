# vim:fileencoding=utf8
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.plasma import Plasma
from PyKDE4.kdeui import *
from PyKDE4 import plasmascript
from xmlrpclib import ServerProxy
import socket
 
class AlarmClock(plasmascript.Applet):
    def __init__(self,parent,args=None):
        plasmascript.Applet.__init__(self,parent)
        socket.setdefaulttimeout(0.5)
        self.alarmserver = ServerProxy("http://10.42.3.2:8000")
        self.reset()
 
    def init(self):
        self.setHasConfigurationInterface(False)
        self.setAspectRatioMode(Plasma.IgnoreAspectRatio)

        self.theme = Plasma.Svg(self)
        self.theme.setImagePath("widgets/background")
        self.setBackgroundHints(Plasma.Applet.DefaultBackground)

        self.layout = QGraphicsGridLayout(self.applet)
        self.hour_lbl = Plasma.Label(self.applet)
        self.hour_lbl.setAlignment(Qt.AlignCenter)
        self.hour_lbl.setText("%02d" % self.hour)
        self.layout.addItem(self.hour_lbl, 1, 1)

        #print self.layout.setRowPreferredHeight(1, 20)

        self.minute_lbl = Plasma.Label(self.applet)
        self.minute_lbl.setText("%02d" % self.minute)
        self.minute_lbl.setAlignment(Qt.AlignCenter)
        self.layout.addItem(self.minute_lbl, 1, 2)

        h_plus = Plasma.PushButton(self.applet)
        h_plus.setStyleSheet("color: black")
        h_plus.nativeWidget().setIcon(KIcon("arrow-up"))
        self.layout.addItem(h_plus, 0, 1)
        m_plus = Plasma.PushButton(self.applet)
        m_plus.nativeWidget().setIcon(KIcon("arrow-up"))
        m_plus.setStyleSheet("color: black")
        self.layout.addItem(m_plus, 0, 2)
        h_minus = Plasma.PushButton(self.applet)
        h_minus.nativeWidget().setIcon(KIcon("arrow-down"))
        h_minus.setStyleSheet("color: black")
        self.layout.addItem(h_minus, 2, 1)
        m_minus = Plasma.PushButton(self.applet)
        m_minus.nativeWidget().setIcon(KIcon("arrow-down"))
        m_minus.setStyleSheet("color: black")
        self.layout.addItem(m_minus, 2, 2)


        self.cb = Plasma.CheckBox()
        self.layout.addItem(self.cb, 1, 0)
        self.cb.nativeWidget().setIcon(KIcon("user-busy"))
        self.cb.setChecked(self.enabled)

        self.timer = QTimer()
        self.connect(self.timer, SIGNAL("timeout()"), self.update_time)
        self.timer.start(20000)

        self.connect(self.cb, SIGNAL("toggled(bool)"), self.change_enabled)

        self.connect(h_plus, SIGNAL("clicked()"), self.hour_plus)
        self.connect(h_minus, SIGNAL("clicked()"), self.hour_minus)
        self.connect(m_plus, SIGNAL("clicked()"), self.minute_plus)
        self.connect(m_minus, SIGNAL("clicked()"), self.minute_minus)

        self.setLayout(self.layout)
        self.update_time()
        #self.resize(125, 125)


    def reset(self):
        (self.hour, self.minute, self.enabled) = (-1, -1, False)

    def change_enabled(self, value):
        try:
            self.alarmserver.enable(value)
            self.enabled = self.alarmserver.enabled()
        except socket.error:
            self.reset()
        self.update_time()

    def hour_plus(self):
        self.hour += 1
        self.set_alarm()

    def hour_minus(self):
        self.hour -= 1
        self.set_alarm()

    def minute_plus(self):
        self.minute += 1
        self.set_alarm()

    def minute_minus(self):
        self.minute -= 1
        self.set_alarm()

    def set_alarm(self):
        if self.hour < 0:
            self.hour = 23
        elif self.hour > 23:
            self.hour = 0
        if self.minute < 0:
            self.minute = 59
        elif self.minute > 59:
            self.minute = 0
        try:
            self.alarmserver.set(self.hour, self.minute)
            self.alarmserver.enable(self.enabled)
        except socket.error:
            self.reset()
        self.update_time()


    def update_time(self):
        try:
            (self.hour, self.minute) = self.alarmserver.time()
            self.enabled = self.alarmserver.enabled()
        except socket.error:
            self.reset()

        if -1 in (self.hour, self.minute):
            self.hour_lbl.setText("Err")
            self.minute_lbl.setText("Err")
        else:
            self.hour_lbl.setText("%02d" % self.hour)
            self.minute_lbl.setText("%02d" % self.minute)

        self.cb.setChecked(self.enabled)
        if self.enabled:
            self.cb.nativeWidget().setIcon(KIcon("user-online"))
        else:
            self.cb.nativeWidget().setIcon(KIcon("user-busy"))


 
 
def CreateApplet(parent):
    return AlarmClock(parent)
