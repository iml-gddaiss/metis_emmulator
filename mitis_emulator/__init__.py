import os
import shutil
import click
from pathlib import Path

CONFIG_FILE_NAME = "mitis_config.json"
DEFAULT_CONFIGURATION_FILE = Path(__file__).resolve().parent.joinpath(CONFIG_FILE_NAME).resolve()
LOCAL_CONFIGURATION_FILE = Path(os.getenv('HOME') + '/.' + CONFIG_FILE_NAME)


def init_local_file(force=False):
    if not Path(LOCAL_CONFIGURATION_FILE).is_file() or force is True:
        shutil.copyfile(DEFAULT_CONFIGURATION_FILE, LOCAL_CONFIGURATION_FILE)
        click.secho(f'Initializing done...', fg='green')
        click.secho(f'Configration files at: {LOCAL_CONFIGURATION_FILE}', fg='yellow')
    else:
        click.secho(f'Configuration files already exists.', fg='red')
        click.secho(f'Configration files at: {LOCAL_CONFIGURATION_FILE}', fg='yellow')

