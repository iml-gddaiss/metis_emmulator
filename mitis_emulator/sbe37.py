"""
Author: jerome.guay@protonmail.com
Date: August 2023


Notes
-----

From Controller Firmware:

    SerialOut ( ComPort, OutString, WaitString, NumberTries, TimeOut )
    SerialIn(dest, Comport, Timeout, TerminationChar, MaxNumChars)

    Start:
      # wait for the "S>" which mean it's ready for a new command
      SerialOut(SerialSBE37,CHR(13),"S>",1,50)
      SerialOut(SerialSBE37,"ts"&CHR(13)," ",1,400)
      SerialIn(RawSBE37_SalinityTest,SerialSBE37,300,CHR(83),40)

    Collect:
      SerialOut(SerialSBE37,CHR(13),"S>",1,50)

      If X = 1 Then
        SerialOut(SerialSBE37,"tss"&CHR(13)," ",1,400)
      Else
        SerialOut(SerialSBE37,"sl"&CHR(13)," ",1,400)
      EndIf

      SerialIn(RawSBE37,SerialSBE37,400,83,60)

From Seabird
    S> :After Seaterm232 displays the GetHD response, it provides an S> prompt
        to indicate it is ready for the next command
    ts: Take sample, store data in buffer, output data:
        string: 23.7658, 0.00019, 0.062, 20 Oct 2012, 00:51:30
                temp, conduct, pres (db), date, time
    tss: Take new sample, store data in buffer and in
        FLASH memory, and output data.
        Note: MicroCAT ignores this command if
        sampling data (Start has been sent).
        string: 23.7658, 0.00019, 0.062, 20 Oct 2012, 00:51:30
                temp, conduct, pres (db), date, time

    sl: Send Last Stored Value

"""

import time
import threading
import serial

from .logger import make_logger

import logging


class SBE37:
    beaudrate =19_200
    timeout = .1
    binary_format = 'ascii'
    buffer_size = 1
    clock_speed = .1
    transmit_sleep = 0.01

    def __init__(self, debug=False):
        log_level = logging.INFO
        if debug is True:
            log_level = logging.DEBUG

        self.log = make_logger(self.__class__.__name__, level=log_level)

        self.serial: serial.Serial = None
        self.thread: threading.Thread = None

        self._is_running = False

        self.receive_msg = ""
        self.sample_buffer = ""
        self.make_sample(low_salinity=False)
        self.log.info(f'Sampled data (len: {len(self.sample_buffer)}): {self.sample_buffer}')

    @property
    def is_running(self):
        return self._is_running

    def open_serial(self, port):
        self.log.info(f'Opening port: {port}')

        self.serial = serial.Serial()
        self.serial.baudrate = self.beaudrate
        self.serial.timeout = self.timeout
        self.serial.port = port

        self.serial.open()

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

            buff = self.serial.read(self.buffer_size).decode(self.binary_format)

            if buff == "":
                continue

            if buff != "\r":
                self.log.debug(f'Buffer: {buff}')
                self.receive_msg += buff
                continue

            self.log.info(f'Message received: {self.receive_msg}')

            _match = self.receive_msg.lower()

            if _match == "":
                self.transmit_delay()
                self.send_ready_msg()
            elif _match in ["ts", "tss", "sl"]:
                self.transmit_delay()
                self.echo()
                self.send_sample()
                self.send_ready_msg()
            else:
                self.log.warning(f"Received Unexpected {self.receive_msg}")

            self.receive_msg = ''

    def transmit_delay(self):
        """
        Notes
        -----
            Unsure if it necessary
        """
        time.sleep(self.transmit_sleep)

    def send(self, msg: str, end_char=True):
        if end_char:
            msg += "\r\n"
        self.serial.write((msg).encode(self.binary_format))
        self.log.info(rf'`{msg}` sent')

    def echo(self):
        """Send back the received message"""
        self.log.info('Echoing message')
        self.send(self.receive_msg, end_char=True)

    def send_sample(self):
        self.log.info('Sending Sample')
        self.send(self.sample_buffer, end_char=True)

    def send_ready_msg(self):
        self.log.info('Sending Ready Message')
        self.send("S>", end_char=False)
        # self.serial.write("S>".encode(self.binary_format))

    def close(self):
        self.log.info('Closing Serial')
        self._is_running = False

        self.log.info('Waiting for thread ...')
        self.thread.join()

        self.serial.close()
        self.log.info('Serial Closed')

    def make_sample(self, low_salinity=False):
        """
        String total length: 38
        Strings Format:
            temperature:  tttt.tttt (4.4)
            conductivity:  cc.ccccc (2.5)
            salinity:     ssss.ssss (4.4)
            density:       rrr.rrrr (3.4)
        """
        temperature = '  23.7658'
        conductivity = '  0.00019'
        salinity = '   0.0000' if low_salinity else '  30.1234'
        density = ' 28.1234'

        self.sample_buffer = ','.join([temperature, conductivity, salinity, density])


def start_SBE37(port: str, debug=False):
    sbe37 = SBE37(debug=debug)
    sbe37.start(port=port)

    return sbe37


if __name__ == '__main__':
    port = '/dev/ttyUSB3'
    s = start_SBE37(port=port)

