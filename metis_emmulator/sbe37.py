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

import logging

import time
import datetime

import socket
import threading

import serial

import random


BEAUDERATE = 19200
TIMEOUT = 10
BINARY_FORMAT = 'ascii'
BUFFER_SIZE = 2048

SLEEP_DELAY = .1

logger = logging.getLogger()
logger.setLevel('DEBUG')


class SBE37:
    def __init__(self):
        self.serial: serial.Serial = None

        self.thread: threading.Thread = None

        self.is_running = False
        self.do_sampling = False

        self.sample_buffer = ""

    def start(self, port):
        logging.info(f'Starting SBE 37 on port: {port}')

        self.serial = serial.Serial()
        self.serial.baudrate = BEAUDERATE
        self.serial.port = port
        self.serial.timeout = TIMEOUT

        self.serial.open()

        if self.serial.is_open:
            self.is_running = True
            self.thread = threading.Thread(target=self.run, daemon=False)
            self.thread.start()

    def run(self):
        logging.info(f"Running SBE 37")

        while self.is_running:
            _received = self.serial.read(BUFFER_SIZE).decode(BINARY_FORMAT)
            if _received:
                logging.debug(f"Raw received: {_received}")
                logging.info(f'Received: {_received}')

                match _received:
                    case "\r":
                        self.send_ready_msg()
                    case "ts\r":
                        self.make_sample()
                        self.send_data()
                    case "tss\r":
                        self.make_sample()
                        self.send_data()
                    case "sl\r":
                        logging.debug('`sl` received FIXME') #TODO
                    case _ :
                        pass

            time.sleep(SLEEP_DELAY)

    def make_sample(self):
        current_time = datetime.datetime.now()
        date = current_time.strftime("%d %b %Y")
        _time = current_time.strftime("%H:%M:%S")
        _temp = 24 * random_variation()
        _cond = 0.0002 * random_variation()
        _pres = 0.05 * random_variation()
        self.sample_buffer = f"{_pres:.4f}, {_cond:.5f}, {_pres:.3f}, {date}, {_time}"
        logging.info(f'Sampled data: {self.sample_buffer}')


    def send_space_char(self):
        self.serial.write(' '.encode(BINARY_FORMAT))
        logging.info('Return Carriage sent')

    def send_ready_msg(self):
        self.serial.write('S>'.encode(BINARY_FORMAT))
        logging.info('Ready Message sent')

    def send_data(self):
        self.serial.write(self.sample_buffer.encode(BINARY_FORMAT))
        logging.info('Data sent')
        time.sleep(SLEEP_DELAY)

    def close(self):
        logging.info('Closing Serial')
        self.is_running = False
        logging.info('Waiting for thread ...')
        self.thread.join()
        self.serial.close()
        logging.info('Serial Closed')

    # TODO
    # def send_junk ?


def random_variation():
    return 1 + (random.random() - .5) / 10


def start_SBE37(port=None):
    sbe37 = SBE37()
    sbe37.start(port)
    return sbe37


if __name__ == '__main__':
    sbe37 = start_SBE37(port='/dev/tty2')
