import click
import serial

from .utils import get_serial_ports, test_serial_port
from .sbe37 import start_SBE37


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
def sbe37(port):
    try:
        start_SBE37(port)
    except serial.SerialException:
        click.secho(f'Port `{port}` does not exist.', fg='red')


if __name__ == "__main__":
    root()



