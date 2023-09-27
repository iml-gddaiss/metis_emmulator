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
2023/09/27 12:33:00.00 00016
Hdg: 330.8 Pitch: 0.1 Roll: 0.5
Temp: 23.9 SoS: 1528 BIT: 00
Bin    Dir    Mag     E/W     N/S    Vert     Err   Echo1  Echo2  Echo3  Echo4
  1    --      --     -41     124     -34  -32768     48     55     56     39
...
 25    --      --  -32768  -32768  -32768  -32768     40     46     43     41

```

"""


class WorkHorse:
    beaudrate = 115200
    binary_format = 'ascii'
    buffer_size = 3000
    number_of_bins = 25

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
        self.make_data_string(nbin=self.number_of_bins)

    @property
    def is_running(self):
        return self._is_running

    def open_serial(self, port):
        self.log.info(f'Opening port: {port}')

        self.serial = serial.Serial()
        self.serial.bytesize = serial.EIGHTBITS
        self.serial.parity = serial.PARITY_NONE
        self.serial.stopbits = serial.STOPBITS_ONE
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
        self.log.info(f'Sample Interval: {self.sampling_rate}s')

        while self._is_running:
            self.send_data()
            time.sleep(self.sampling_rate)

    def send(self, msg: str, end_char=True):
        if end_char:
            msg += "\n\n"
        self.log.info("```" + msg + "```")
        self.serial.write(msg.encode(self.binary_format))
        # self.log.info(rf'`{msg}` sent')

    def send_data(self):
        self.log.info(f'Sampled sent. (Interval: {self.sampling_rate}s)')
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
            "2023/09/27 12:33:00.00 00016",
            "Hdg: 330.8 Pitch: 0.1 Roll: 0.5",
            "Temp: 23.9 SoS: 1528 BIT: 00",
            "Bin    Dir    Mag     E/W     N/S    Vert     Err   Echo1  Echo2  Echo3  Echo4",
        ]
        for i in range(nbin):
            # _sample.append(f" {i+1} -- -- -32768 -32768 -32768 -32768 43 49     46      43")
            _sample.append(f" {i+1:>2}    --      --  -32768  -32768  -32768  -32768     40     46     43     41")

        self.data_string = "\n".join(_sample)


def start_workhorse(port: str, sampling_rate=int, debug=False):
    workhorse = WorkHorse(debug=debug, sampling_rate=sampling_rate)
    workhorse.start(port=port)

    return workhorse


if __name__ == '__main__':
    port = '/dev/ttyUSB3'
    s = start_workhorse(port=port)
