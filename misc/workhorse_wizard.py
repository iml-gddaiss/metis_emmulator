import sys

import serial
import time
from datetime import datetime, timedelta

ENCODING = "ascii"

class Wizard:
    def __init__(self, port: str, bauderate):
        self.serial = serial.Serial()
        self.serial.bytesize = serial.EIGHTBITS
        self.serial.parity = serial.PARITY_NONE
        self.serial.stopbits = serial.STOPBITS_ONE
        self.serial.baudrate = bauderate
        self.serial.port = port
        self.serial.open()
        self.serial.timeout = .1

    def enter_command_mode(self):
        self.serial.send_break()
        time.sleep(1)
        try:
            answer = self.serial.read_all().decode(ENCODING)
            print(answer)
        except UnicodeError:
            print("NO RETURN: Wrong Bauderate")
            sys.exit()

    def send(self, command: str, value: str = ""):
        self.serial.write((command + value + '\r').encode(ENCODING))
        time.sleep(1)
        try:
            answer = self.serial.read_all().decode(ENCODING)
            print(answer)
        except UnicodeError:
            print("NO RETURN: Bauderate change")

    def set_serial_control(self, bauderate: int = 9600, parity: str = None, stop_bit: int = 1):
        """
        Baud Rate          Parity                      Stop Bits
        0 = 300
        1 = 1200           1 = None (Default)          1 = 1 Bit (Default)
        2 = 2400           2 = Even                    2 = 2 Bits
        3 = 4800           3 = Odd
        4 = 9600 (Default) 4 = Low (Space, logical 0)
        5 = 19200          5 = High (Mark, logical 1)
        6 = 38400
        7 = 57600
        8 = 115200
        """
        bauderates = [300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
        parities = [None, "even", "odd", "low", "high"]

        value = str(bauderates.index(bauderate)) + str(parities.index(parity) + 1) + str(stop_bit)

        self.send("CB", value)

    def set_flow_control(self, ens=1, ping=1, output=0, serial=0, record=1):
        """
        ens:
             1: Automatic Ensemble Cycling – Automatically starts the next data collection cycle after
               the current cycle is completed. Only a <BREAK> can stop this cycling.
             0: Manual Ensemble Cycling – Enters the STANDBY mode after transmission of the data
               ensemble, displays the “>” prompt and waits for a new command.
        ping:
             1: Automatic Ping Cycling – Pings immediately when ready.
             0: Manual Ping Cycling – Sends a < character to signal ready to ping, and then waits to
                receive an <Enter> before pinging. The <Enter> sent to the WorkHorse ADCP is not
                echoed. This feature lets you manually control ping timing within the ensemble.
        output:
             2: Hex-ASCII Data Output, Carriage Return-Linefeed delimited -- Sends the ensemble in
                readable hexadecimal-ASCII format with a Carriage Return-Linefeed at the end of each
                ensemble, if serial output is enabled (see below).
             1: Binary Data Output – Sends the ensemble in binary format, if serial output is enabled
                (see below).
             0: Hex-ASCII Data Output – Sends the ensemble in readable hexadecimal-ASCII format, if
                serial output is enabled (see below).
        serial:
             1: Enable Serial Output – Sends the data ensemble out the RS-232/422 serial interface.
             0: Disable Serial Output – No ensemble data are sent out the RS-232/422 interface.
        Record:
            1: Enable Data Recorder – Records data ensembles on the recorder (if installed).
            0: Disable Data Recorder – No data ensembles are recorded on the recorder. 
        """
        self.send("CF", f"{ens}{ping}{output}{serial}{record}")

    def output_pd8(self):
        self.send('PD', "8")

    def set_real_time(self):
        real_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
        self.send("TT", real_time)

    def set_start_time(self, value: str):
        """yyyy/mm/dd, HH:MM:SSS"""
        self.send("TG", value)

    def set_ping_per_ensemble(self, value: int):
        self.send("WP", f"{value:05d}")

    def set_time_between_pings(self, value: str):
        """ MM:SS.ss"""
        self.send("TP", value)

    def set_time_between_ensemble(self, value: str):
        """HH:MM:SS.ss"""
        self.send("TE", value)

    def set_number_of_cells(self, value: int):
        self.send("WN", f"{value:03d}")

    def keep_parameters(self):
        self.send("CK")

    def retrieve_parameters(self, value: int):
        """value: (0: user, 1: factory)"""
        self.send("CR", f"{value}")

    def deploy(self):
        self.send("CS")

    def power_down(self):
        self.send("CZ")

    def close(self):
        self.serial.close()


def pd8_test_setup(port, bauderate, new_bauderate = None):
    start_time = (datetime.now() + timedelta(seconds=60)).strftime("%Y/%m/%d, %H:%M:%S")

    w = Wizard(port=port, bauderate=bauderate)
    w.enter_command_mode()

    if new_bauderate is None:
        new_bauderate = bauderate

    w.set_serial_control(bauderate=new_bauderate, parity=None, stop_bit=1)

    if new_bauderate != bauderate:
        w.close()
        w = Wizard(port=port, bauderate=new_bauderate)

    w.set_flow_control(ens=1, ping=1, output=1, serial=1, record=1)
    #w.output_pd8()
    w.set_real_time()
    w.set_number_of_cells(27)
    w.set_ping_per_ensemble(1)
    w.set_time_between_pings("00:00.50")
    w.set_time_between_ensemble("00:10:00.00")
    w.set_start_time(start_time)
    w.keep_parameters()
    w.deploy()
    w.close()


def power_down(port, bauderate):
    w = Wizard(port, bauderate)
    w.enter_command_mode()
    w.power_down()
    w.close()


if __name__ == "__main__":
    PORT = "/dev/ttyUSB3"
    current_bauderate = [115200, 19200][0]
    pd8_test_setup(port=PORT, bauderate=current_bauderate, new_bauderate=115200)
    #power_down(port=PORT, bauderate=current_bauderate)
