from dataclasses import dataclass
from . import LOCAL_CONFIGURATION_FILE, init_local_file
from .utils import json2dict
from .sbe37 import SBE37
from .adcp_workhorse import WorkHorse

# replace by and INI file

@dataclass
class Ports:
    sbe37: str
    workhorse: str


init_local_file(silent=True)

CONFIGURATION = json2dict(LOCAL_CONFIGURATION_FILE)


PORTS = Ports(**CONFIGURATION['ports'])


class VirtualDevices:
    def __init__(self, debug=False):
        self.sbe37 = SBE37(debug=debug)
        self.workhorse = WorkHorse(
            debug=debug,
            sampling_rate=CONFIGURATION["workhorse_sampling_rate_s"]
        )


def start_devices(debug=False):
    virtual_devices = VirtualDevices(debug=debug)

    virtual_devices.sbe37.start(port=PORTS.sbe37)

    virtual_devices.workhorse.start(port=PORTS.workhorse)

    return virtual_devices


if __name__ == "__main__":
    virtual_devices = start_devices()