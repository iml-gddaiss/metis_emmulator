from .sbe37 import SBE37
from .adcp_workhorse import WorkHorse

# replace by and INI file
class Ports:
    sbe37 = '/dev/ttyUSB3'
    workhorse = '/dev/ttyUSB2'


class VirtualDevices:
    def __init__(self, debug=False):
        self.sbe37 = SBE37(debug=debug)
        self.workhorse = WorkHorse(debug=debug)


def start_devices(debug=False):
    virtual_devices = VirtualDevices(debug=debug)

    virtual_devices.sbe37.start(port=Ports.sbe37)

    virtual_devices.workhorse.start(port=Ports.workhorse)

    return virtual_devices


if __name__ == "__main__":
    virtual_devices = start_devices()