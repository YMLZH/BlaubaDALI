# blaubadali/luba.py for DALI communcation based on config.py
import serial
import time

class LubaInterface:
    def __init__(self, port="/dev/ttyACM0", baud=115200):
        self.ser = serial.Serial(port, baud, timeout=0.2)
        self.tx_buffer = []

        # LUBA CMDs
        self.CMD_ADD_16BIT = 0x34

    def build_frame(self, cmd, data):
        SYNC = 0x59
        length = len(data)
        cs = cmd ^ length
        for b in data:
            cs ^= b
        return bytes([SYNC, cmd, length] + data + [cs])

    def send(self, cmd, data):
        frame = self.build_frame(cmd, data)
        self.tx_buffer.append(frame)
        return frame

    def execute_tx_buffer(self):
        for frame in self.tx_buffer:
            self.ser.write(frame)
            time.sleep(0.05)
        self.tx_buffer.clear()
        return b"sent"

    def clear_tx_buffer(self):
        self.tx_buffer.clear()

    def dali_group(self, group, level):
        LINE_INDEX = 0x00
        MODE = 0x00
        return [LINE_INDEX, MODE, (0x80 | (group << 1)), level]

    def close(self):
        self.ser.close()
