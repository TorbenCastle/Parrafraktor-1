import serial
import threading

class SerialDMX():
    def __init__(self, port, baudrate, timeout):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._data_lock = threading.Lock()
        self._dmx_data = bytearray(512)  # Assuming DMX standard packet size is 512 bytes
        self._serial = 1 #serial.Serial(port, baudrate, timeout=timeout)
        self._reading_thread = threading.Thread(target=self._read_serial)
        self._stop_reading = threading.Event()

    def start(self):
        self._reading_thread.start()

    def stop(self):
        self._stop_reading.set()
        self._reading_thread.join()
        self._serial.close()

    def get_dmx_data(self):
        with self._data_lock:
            return bytes(self._dmx_data)

    def get_channel_value(self, channel):
        with self._data_lock:
            return self._dmx_data[channel - 1]  # Channels are 1-indexed

    def _read_serial(self):
        while not self._stop_reading.is_set():
            data = 1
            #data = self._serial.read(512)
            
            with self._data_lock:
                self._dmx_data = data
