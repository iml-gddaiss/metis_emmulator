from .sbe37 import SBE37


class Ports:
    sbe37 = '/dev/ttyUSB3'



class VirtualDevices:
    def __init__(self, debug=False):
        self.sbe37 = SBE37(debug=debug)


def start_devices(debug=False):
    virtual_devices = VirtualDevices(debug=debug)

    virtual_devices.sbe37.start(port=Ports.sbe37)

    return virtual_devices


if __name__ == "__main__":
    virtual_devicers = start_devices()