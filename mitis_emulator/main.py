import click
import serial

from .utils import get_serial_ports, test_serial_port
from .server import start_devices
from .sbe37 import start_SBE37
from .adcp_workhorse import start_workhorse


@click.group('root')
def root():
    pass


@root.group('ports')
def serial_ports():
    pass


@serial_ports.command('test')
@click.argument('port', type=click.STRING)
@click.argument('msg', type=click.STRING)
def _test_serial_port(port, msg='test'):
    test_serial_port(port, msg)


@serial_ports.command('list')
def list_serial_ports():
    serial_ports = get_serial_ports()
    if len(serial_ports) < 1:
        click.secho('No serial port found.', fg='red')
    else:
        click.secho('Serial ports found !', fg='green')
        for port in serial_ports:
            click.echo(f'{port}')


@root.group('start')
def start():
    pass


@start.command('sbe37')
@click.argument('port', type=click.STRING)
@click.option('-d', '--debug', is_flag=True)
def sbe37(port, debug):
    try:
        start_SBE37(port=port, debug=debug)
    except serial.SerialException:
        click.secho(f'Port `{port}` does not exist.', fg='red')

@start.command('workhorse')
@click.argument('port', type=click.STRING)
@click.option('-d', '--debug', is_flag=True)
def sbe37(port, debug):
    try:
        start_workhorse(port=port, debug=debug)
    except serial.SerialException:
        click.secho(f'Port `{port}` does not exist.', fg='red')

@start.command('devices')
@click.option('-d', '--debug', is_flag=True)
def devices(debug):
    # try:
    #     _ = start_devices(debug=debug)
    # except serial.SerialException:
    #     click.secho(f'One of the ports does not exist.', fg='red')

    _ = start_devices(debug=debug)


if __name__ == "__main__":
    root()



