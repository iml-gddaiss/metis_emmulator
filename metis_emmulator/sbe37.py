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

    sl ????? Sent by the controller

"""

import time
import datetime
import threading
import serial
import random

from typing import Optional

from logger import make_logger

import logging
LOGGER_LEVEL = logging.DEBUG


class SBE37:
    """
    TODO def send_junk ?
    """
    beaudrate =19_200
    timeout = 10
    binary_format = 'ascii'
    buffer_size = 2_048
    run_sleep = .1
    send_sleep = .1

    def __init__(self):
        self.log = make_logger(self.__class__.__name__, level=LOGGER_LEVEL)

        self.serial: serial.Serial = None

        self.thread: threading.Thread = None

        self.is_running = False
        self.do_sampling = False

        self.sample_buffer = ""

    def start(self, port):
        self.log.info(f'Starting on port: {port}')

        self.serial = serial.Serial()
        self.serial.baudrate = self.beaudrate
        self.serial.port = port
        self.serial.timeout = self.timeout

        self.serial.open()

        if self.serial.is_open:
            self.is_running = True
            self.thread = threading.Thread(target=self.run, daemon=False)
            self.thread.start()

    def run(self):
        self.log.info(f"Running ...")

        while self.is_running:
            _received = self.serial.read(self.buffer_size).decode(self.binary_format)
            if _received:
                self.log.debug(f"Raw received: {_received}")

                match _received:
                    case "\r":
                        self.send_ready_msg()
                    case "ts\r" | "tss\r":
                        self.make_sample()
                        self.send_sample()
                    case "sl\r":
                        self.log.debug('`sl` received FIXME') #TODO
                    case _:
                        self.log.warning(f'Unexpected received: {_received}')

            time.sleep(self.run_sleep)

    def make_sample(self):
        current_time = datetime.datetime.now()
        date = current_time.strftime("%d %b %Y")
        _time = current_time.strftime("%H:%M:%S")
        _temp = 24 * random_variation()
        _cond = 0.0002 * random_variation()
        _pres = 0.05 * random_variation()
        self.sample_buffer = f"{_pres:.4f}, {_cond:.5f}, {_pres:.3f}, {date}, {_time}"
        self.log.info(f'Sampled data: {self.sample_buffer}')

    def send_space_char(self):
        self.log.info('Sending Space Character')
        self.send_message(' ')

    def send_ready_msg(self):
        self.log.info('Sending Ready Message `S>`')
        self.send_message('S>')

    def send_sample(self):
        self.log.info('Sending Sample')
        self.send_message(self.sample_buffer)

    def send_message(self, msg: str):
        _result = self.serial.write(msg.encode(self.binary_format))
        if _result:
            self.log.warning(f'Sending Failed. Serial Write Result: {_result}')
        else:
            self.log.info(f'`{msg}` sent')
        time.sleep(self.send_sleep)

    def close(self):
        self.log.info('Closing Serial')
        self.is_running = False

        self.log.info('Waiting for thread ...')
        self.thread.join()

        self.serial.close()
        self.log.info('Serial Closed')


def random_variation():
    return 1 + (random.random() - .5) / 10


def start_SBE37(port: str):
    sbe37 = SBE37()
    sbe37.start(port=port)

    return sbe37


if __name__ == '__main__':
    sbe37 = start_SBE37(port='/dev/tty2')
