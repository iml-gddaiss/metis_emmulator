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
LOGGER_LEVEL = logging.INFO


class SBE37:
    beaudrate =19_200
    timeout = .1
    binary_format = 'ascii'
    buffer_size = 1
    run_sleep = .001
    send_sleep = .001

    def __init__(self):
        self.log = make_logger(self.__class__.__name__, level=LOGGER_LEVEL)

        self.serial: serial.Serial = None

        self.thread: threading.Thread = None

        self.is_running = False
        self.do_sampling = False

        self.receive_msg = b""
        self.sample_buffer = ""
        self.make_sample()

    def make_sample(self):
        _temp = '  23.7658'  # tttt.tttt
        _cond = '  0.00019'  # cc.ccccc
        _psal = '   9.1234' # ssss.ssss
        # _psal = '  30.1234'  # ssss.ssss
        _dens = ' 28.1234'  # rrr.rrrr
        self.sample_buffer = ','.join([_temp, _cond, _psal, _dens])
        self.log.info(f'Sampled data (len: {len(self.sample_buffer)}): {self.sample_buffer}')

    def open(self, port):
        self.log.info(f'Opening port: {port}')

        self.serial = serial.Serial()
        self.serial.baudrate = self.beaudrate
        self.serial.port = port

        self.serial.open()

    def start(self, port):
        self.open(port)

        if self.serial.is_open:
            self.is_running = True
            self.thread = threading.Thread(target=self.run, daemon=False)
            self.thread.start()

    def run(self):
        self.log.info(f"Running ...")

        while self.is_running:
            buff = self.serial.read(self.buffer_size).decode(self.binary_format)
            self.log.debug(f'Buffer: {buff}')

            if buff != '\r':
                self.receive_msg += buff
            else:
                self.log.info(rf'Message received: {self.receive_msg}')

                match = self.receive_msg.lower()

                if match == "":
                    self.send_ready_msg()
                elif match == "ts" | "tss":
                    self.echo()
                    self.send_sample()
                    self.send_ready_msg()
                elif match == "sl":
                    self.echo()
                    self.send_sample()
                    self.send_ready_msg()
                else:
                    self.log.warning(f"Received Unexpected {self.receive_msg}")

                self.receive_msg = ''

            time.sleep(self.run_sleep)

    def send(self, msg: str):
        self.serial.write((msg + "\r\n").encode(self.binary_format))
        self.log.info(f'`{msg}` sent')
        time.sleep(self.send_sleep)

    def echo(self):
        """Send back the received message"""
        self.log.info('Echoing message')
        self.send(self.receive_msg)

    def send_sample(self):
        self.log.info('Sending Sample')
        self.send(self.sample_buffer)

    def send_ready_msg(self):
        self.log.info('Sending Ready Message')
        self.serial.write("S>".encode(self.binary_format))

    def close(self):
        self.log.info('Closing Serial')
        self.is_running = False

        self.log.info('Waiting for thread ...')
        self.thread.join()

        self.serial.close()
        self.log.info('Serial Closed')


def start_SBE37(port: str):
    sbe37 = SBE37()
    sbe37.start(port=port)

    return sbe37


if __name__ == '__main__':
    port = '/dev/ttyUSB0'
    s = start_SBE37(port='/dev/ttyUSB0')
    # s = SBE37()
    # s.open(port=port)
