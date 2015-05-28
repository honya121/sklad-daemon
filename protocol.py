class protocol_t:
    def __init__(self, output):
        self.output = output
        self.state = 0
        self.packet_num = 0
        self.cmd = 0
        self.rec_packet_num = 0
        self.expected_length = 0
        self.argv = []
        self.rec_error = 0
        self.cmd_process = {}
        self.responce_process = {}

    def clear(self):
        self.state = 0
        self.packet_num = 0
        self.argv = []
        self.responce_process = {}

    def send(self, cmd, args = [], responce_process = None):
        self.packet_num += 1
        if self.packet_num == 256:
            self.packet_num = 1
        self.responce_process[self.packet_num] = [responce_process, cmd]
        packet = [0x80, self.packet_num, cmd]
        packet.extend(args)
        self.output(''.join(chr(i) for i in packet))
        return self.packet_num

    def send_ack(self, packet_num, args = []):
        packet = [0x80, packet_num, 0x01, len(args)]
        packet.extend(args)
        self.output(''.join(chr(i) for i in packet))

    def send_nack(self, packet_num, error_code, args = []):
        packet = [0x80, packet_num, 0x00, error_code]
        packet.extend(args)
        self.output(''.join(chr(i) for i in packet))

    def parse(self, data):
        for b in data:
            if self.state == 0: # start byte
                if b == 0x80:
                    self.state = 1
            elif self.state == 1: # packet number
                self.rec_packet_num = b
                self.state = 2
            elif self.state == 2: # cmd
                self.cmd = b
                if self.cmd == 0x00 or self.cmd == 0x01: # NACK or ACk
                    self.state = 3
                elif self.cmd == 0x08: # log message
                    self.argv = ''
                    self.state = 5
                else:
                    self.state = 0
            elif self.state == 3: # NACK.error_number or ACK.length
                if self.cmd == 0x00: # NACK
                    self.rec_error = b
                    if self.rec_error == 0x00: # unknown cmd
                        self.expected_length = 1
                        self.state = 4
                    elif self.rec_error == 0x06: # power source locked
                        self.expected_length = 2
                        self.state = 4
                    else:
                        self._call_responce()
                elif self.cmd == 0x01: # ACK
                    self.expected_length = b
                    self.state = 4
                    if self.expected_length == 0:
                        self._call_responce()
                else:
                    self.state = 0
            elif self.state == 4:
                self.argv.append(b)
                self.expected_length -= 1
                if self.expected_length == 0:
                    self._call_responce()
            elif self.state == 5: # log message
                if b != 0:
                    self.argv += chr(b)
                else:
                    self._call_cmd()
            else:
                self.state = 0

    def set_cmd_process(self, cmd, process):
        self.cmd_process[cmd] = process

    def _call_responce(self):
        if self._call_callback(self.responce_process, self.rec_packet_num, True):
            del self.responce_process[self.rec_packet_num]


    def _call_cmd(self):
        self._call_callback(self.cmd_process, self.cmd)

    def _call_callback(self, table, key, pass_cmd = False):
        ret = False
        if key in table:
            ret = True
            if not pass_cmd:
                proc = table[key]
                if proc != None:
                    proc(self.rec_packet_num, self.argv)
            else:
                proc = table[key]
                if proc[0] != None:
                    proc[0](proc[1], self.rec_packet_num, self.argv)
        self.argv = []
        self.state = 0
        return ret

def get(index):
    if type(index) is list:
        for i in index:
            get(i)
    else:
        packet_num = protocol.send(0x0B, [index], responce_shower)
        print 'sent get({}) settings as packet number {}'.format(index, packet_num)
