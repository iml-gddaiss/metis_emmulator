"""

$GPRMC,193002,V,0000.0000,N,00000.0000,E,,,020109,005.1,W*74

"""


import time
import datetime
import threading
import serial

from mitis_emulator.logger import make_logger

import logging


class GPS:
    beaudrate = 19_200
    timeout = .1
    binary_format = 'ascii'
    buffer_size = 1
    clock_speed = .1
    transmit_sleep = 0.01

    def __init__(self, debug=False):
        self.longitude = -60
        self.latitude = 50
        log_level = logging.INFO
        if debug is True:
            log_level = logging.DEBUG

        self.log = make_logger(self.__class__.__name__, level=log_level)

        self.serial: serial.Serial = None
        self.thread: threading.Thread = None

        self._is_running = False

        self.data_string = ""

    @property
    def is_running(self):
        return self._is_running

    def open_serial(self, port):
        self.log.info(f'Opening port: {port}')

        self.serial = serial.Serial()
        self.serial.baudrate = self.beaudrate
        self.serial.timeout = self.timeout
        self.serial.port = port

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
            time.sleep(self.clock_speed)
            self.send_data()

    def send(self, msg: str, end_char=True):
        if end_char:
            msg += "\r\n"
        self.serial.write(msg.encode(self.binary_format))
        self.log.info(rf'`{msg}` sent')

    def send_data(self):
        self.log.info('Sending Sample')
        self.make_data_string(self)
        self.send(self.data_string, end_char=True)

    def close(self):
        self.log.info('Closing Serial')
        self._is_running = False

    def make_data_string(self):
        """
        $GPRMC,193002,V,0000.0000,N,00000.0000,E,,,020109,005.1,W*74
        """
        now = datetime.datetime.now()

        _date = now.strftime("%d%m%y")
        _time = now.strftime("%H%M%S")

        _lon = str(abs(float(self.longitude))).split('.')
        _lat = str(abs(float(self.latitude))).split('.')

        self.data_string = (f"$GPRMC,{_time},V,"
                            f"{_lat[0]}{60*float('.'+_lat[1]):.2f},"
                            f"{'N' if self.latitude >=0 else 'S'},"
                            f"{_lon[0]}{60*float('.'+_lon[1]):.2f},"
                            f"{'W' if self.longitude >=0 else 'E'}"
                            f",0.000,180,{_date},005.1,W*74")

        self.log.info(f'NMEA: {self.data_string}')


# def start_GPS(port: str, debug=False):
#     gps = GPS(debug=debug)
#     gps.start(port=port)
#
#     return gps


if __name__ == '__main__':
    port = '/dev/ttyUSB3'

    lat, lon = -48.474930, 68.511142
    gps = GPS()
    gps.latitude = lat
    gps.longitude = lon
    gps.make_data_string()