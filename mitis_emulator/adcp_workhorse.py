import time
import threading
import serial

from .logger import make_logger

import logging


"""
WorkHorse:
- Send BREAK signal to enter command mode.
- ADCP will send '>' char in terminal prompt mode (ready to received command).

If the entered command is valid, the WorkHorse ADCP executes the command.
If the command is one that does not provide output data, the WorkHorse ADCP 
sends a carriage return line feed <CR> <LF> and displays a new “>” prompt.

- Send to CE command to received last ensemble sampled.

PD8 output format
Newline CHARs terminate each line and two terminate a ensemble.

```
1997/02/28 11:16:50.07 00001
Hdg: 209.1 Pitch: 9.6 Roll: -9.1
Temp: 22.8 SoS: 1529 BIT: 00
Bin Dir Mag E/W N/S Vert Err Echo1 Echo2 Echo3 Echo4
 1 -- -- -32768 -32768 -32768 -32768 43 49 46 43
 2 -- -- -32768 -32768 -32768 -32768 44 41 45 44
 3 -- -- -32768 -32768 -32768 -32768 43 41 45 43
 4 -- -- -32768 -32768 -32768 -32768 43 41 46 43
 5 -- -- -32768 -32768 -32768 -32768 43 41 45 43
 6 -- -- -32768 -32768 -32768 -32768 42 41 46 43
 7 -- -- -32768 -32768 -32768 -32768 43 42 46 43
 8 -- -- -32768 -32768 -32768 -32768 43 40 46 43
 9 -- -- -32768 -32768 -32768 -32768 43 41 45 44
 10 -- -- -32768 -32768 -32768 -32768 44 41 46 44

```

"""


class WorkHorse:
    beaudrate = 1115200
    binary_format = 'ascii'
    buffer_size = 3000

    def __init__(self, debug=False, sampling_rate=60):
        self.sampling_rate = sampling_rate

        log_level = logging.INFO
        if debug is True:
            log_level = logging.DEBUG

        self.log = make_logger(self.__class__.__name__, level=log_level)

        self.serial: serial.Serial = None
        self.thread: threading.Thread = None

        self._is_running = False

        self.data_string = ""
        self.make_data_string(nbin=25)

    @property
    def is_running(self):
        return self._is_running

    def open_serial(self, port):
        self.log.info(f'Opening port: {port}')

        self.serial = serial.Serial()
        self.serial.baudrate = self.beaudrate
        self.serial.port = port

        self.write_timeout=0

        try:
            self.serial.open()
        except serial.serialutil.SerialException as err:
            self.log.error(f'Ports {err}  does not exist')

    def start(self, port):
        self.open_serial(port)

        if self.serial.is_open:
            self._is_running = True
            self.thread = threading.Thread(target=self.run, daemon=False)
            self.thread.start()

    def run(self):
        self.log.info(f"Running ...")

        while self._is_running:
            self.send_data()
            time.sleep(self.sampling_rate)

    def send(self, msg: str, end_char=True):
        if end_char:
            msg += "\n\n"
        self.serial.write(msg.encode(self.binary_format))
        # self.log.info(rf'`{msg}` sent')

    def send_data(self):
        self.log.info('Sending Sample')
        self.send(self.data_string, end_char=True)

    def close(self):
        self.log.info('Closing Serial')
        self._is_running = False

        self.log.info('Waiting for thread ...')
        self.thread.join()

        self.serial.close()
        self.log.info('Serial Closed')

    def make_data_string(self, nbin=25):
        _sample = [
        "2023/01/01 12:00:00.00 00001",
        "Hdg: 209.1 Pitch: 9.6 Roll: -9.1",
        "Temp: 22.8 SoS: 1529 BIT: 00",
        "Bin Dir Mag E/W N/S Vert Err Echo1 Echo2 Echo3 Echo4",
        ]
        for i in range(nbin):
            _sample.append(f" {i+1} -- -- -32768 -32768 -32768 -32768 43 49 46 43")

        self.data_string = "\n".join(_sample)


def start_workhorse(port: str, sampling_rate=int, debug=False):
    workhorse = WorkHorse(debug=debug, sampling_rate=int)
    workhorse.start(port=port)

    return workhorse


if __name__ == '__main__':
    port = '/dev/ttyUSB3'
    s = start_workhorse(port=port)
