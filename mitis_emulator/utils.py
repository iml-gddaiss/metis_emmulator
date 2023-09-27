import sys
import glob
import serial

import json


def get_serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z0-9]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def test_serial_port(port, msg):
    try:
        ser = serial.Serial()
        ser.port = port
        ser.open()
        ser.write(msg.encode('ascii'))
        ser.close()
    except (ValueError, serial.SerialException):
        print('Port does not exist or is unavailable')


def dict2json(filename: str, dictionary: dict, indent: int = 4) -> None:
    """Makes json file from dictionary

    Parameters
    ----------
    dictionary
    filename
    indent :
        argument is passed to json.dump(..., indent=indent)
    """
    with open(filename, "w") as f:
        json.dump(dictionary, f, indent=indent)


def json2dict(json_file: str):
    """Open json file as a dictionary."""
    with open(json_file) as f:
        dictionary = json.load(f)
    return dictionary
