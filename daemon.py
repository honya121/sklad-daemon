import serial
import database
import protocol
import time

class SkladInterface:
    def __init__(self):
        #self.serial = serial.Serial(0)
        #self.serial = serial.serial_for_url('loop://', timeout=1)
        self.serial = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=3)
        self.protocol = protocol.protocol_t(self.serial.write)
        self.locked = 0
        self.start_pos = 1810
        self.end_pos = 41240
        self.tray_count = 59
        self.writePower()
        self.read()
        time.sleep(4)
        self.writeInit()
        time.sleep(6)
        self.writeMonitorPower()
        self.read()
    def writeMonitorPower(self):
        self.protocol.send(0x07, [0x01], self.responseSended)
        self.locked = 1
    def writeMove(self, pos):
        pos = self.start_pos + ((self.end_pos-self.start_pos)/(self.tray_count-1))*pos
        self.protocol.send(0x02, [pos & 0xFF, (pos>>8) & 0xFF], self.responseSended)
        self.locked = 1
    def writePull(self, len):
        self.protocol.send(0x03, [len & 0xFF, (len>>8) & 0xFF], self.responseSended)
        self.locked = 1
    def writeCut(self):
        self.protocol.send(0x04, [], self.responseSended)
        self.locked = 1
    def writeInit(self):
        self.protocol.send(0x05, [], self.responseSended)
        self.locked = 1
    def writePower(self):
        self.protocol.send(0x06, [0x01], self.responseSended)
        self.locked = 1
    def responseSended(self, packetNum, argv):
        self.locked = 0
    def read(self):
        time.sleep(0.1)
        data = self.serial.read()
        self.protocol.parse(data)

class Daemon:
    def __init__(self):
        self.db = database.Database()
        self.sklad = SkladInterface()
        self.power_indication = PowerIndication()
        print self.db.getFirstCommand()
    def loop(self):
        if self.power_indication.loop():
            self.uninitialize()
            self.power_indication.poweroff()
        self.sklad.read()
        print "Loop"
        command = self.db.getFirstCommand()
        if command:
            print "Novy prikaz"
            result = self.writeCommand(command)
            if result == 0:
                self.db.moveCommand(command[0], -1)
            else:
                print "Sklad error: %d" % (result)
    def writeCommand(self, command):
        print "writing move %d" % (command[5])
        self.sklad.writeMove(command[5])
        time.sleep(1)
        print "writing pull"
        self.sklad.writePull(command[6])
        time.sleep(0.5*command[6])
        print "writing cut"
        self.sklad.writeCut()
        time.sleep(0.5)
        print "finished writing command"
        return 0
    def uninitialize(self):
        pass;
daemon = Daemon()
while True:
    daemon.loop()
