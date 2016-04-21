import protocol

class Device:
    def __init__(self, serial_input, serial_output):
        self.protocol = protocol.protocol_t(serial_output)
        self.serial_output = serial_output
        self.serial_input = serial_input
        self.locked = false
        self.position = 0
        self.expected_position = []
        self.initialized = false
        self.queue = []
        self.length = -1
    def run(self):
        data = self.serial_input.read()
        self.protocol.parse(data)
        self.executeQueue()
    def executeQueue(self):
        if len(self.queue) and self.locked is false:
            row = self.queue[0];
            if row[0] == 0x02:
                packetNum = self.protocol.send(row[0], row[1], self.move_callback)
                self.expected_position[packetNum] = row[1][0] + row[1][1]*256
            elif row[0] == 0x03:
                self.protocol.send(row[0], row[1], self.pull_callback)
            elif row[0] == 0x04:
                self.protocol.send(row[0], row[1], self.cut_callback)
            elif row[0] == 0x05:
                self.protocol.send(row[0], row[1], self.init_callback)
            del row

    def move(self, position):
        self.queue.append([0x02, [position % 256, position // 256]])
    def pull(self, length):
        self.queue.append([0x03, [length % 256, length // 256]])
    def cut(self):
        self.queue.append([0x04, []])
    def init(self):
        self.queue.append([0x05, []])
    def power(self):
        self.queue.append([0x06, []]);

    def move_callback(self, cmd, packetNum, argv):
        self.locked = false;
        self.position = self.expected_position[packetNum]
    def pull_callback(self, cmd, packetNum, argv):
        self.locked = false;
    def cut_callback(self, cmd, packetNum, argv):
        self.locked = false;
    def init_callback(self, cmd, packetNum, argv):
        self.locked = false;
        self.length = argv[0] + argv[1]*256
        self.initialized = true
