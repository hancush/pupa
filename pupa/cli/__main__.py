import sys
import logging
import argparse
import importlib
import traceback
from pupa.core import settings
from pupa.cli.commands.base import CommandError

logger = logging.getLogger('pupa')

COMMAND_MODULES = (
    'pupa.cli.commands.update',
    'pupa.cli.commands.init',
    'pupa.cli.commands.dump',
)


def main():
    parser = argparse.ArgumentParser('pupa', description='pupa CLI')
    parser.add_argument('--debug', nargs='?', const='pdb', default=None,
                        help='drop into pdb (or set =ipdb =pudb)')
    parser.add_argument('--loglevel', default='INFO', help=('set log level. options are: '
                                                            'DEBUG|INFO|WARNING|ERROR|CRITICAL '
                                                            '(default is INFO)'))
    subparsers = parser.add_subparsers(dest='subcommand')

    subcommands = {}
    for mod in COMMAND_MODULES:
        try:
            cmd = importlib.import_module(mod).Command(subparsers)
            subcommands[cmd.name] = cmd
        except ImportError as e:
            logger.error('exception "%s" prevented loading of %s module', e, mod)

    # process args
    args, other = parser.parse_known_args()

    # set log level from command line
    handler_level = getattr(logging, args.loglevel.upper(), 'INFO')
    settings.LOGGING_CONFIG['handlers']['default']['level'] = handler_level
    settings.LOGGING_CONFIG = settings.LOGGING_CONFIG

    # turn debug on
    if args.debug:
        _debugger = importlib.import_module(args.debug)

        # turn on PDB-on-error mode
        # stolen from http://stackoverflow.com/questions/1237379/
        # if this causes problems in interactive mode check that page
        def _tb_info(type, value, tb):
            traceback.print_exception(type, value, tb)
            _debugger.pm()
        sys.excepthook = _tb_info

    if not args.subcommand:
        parser.print_help()
    else:
        try:
            subcommands[args.subcommand].handle(args, other)
        except CommandError as e:
            logger.critical(str(e))


if __name__ == '__main__':
    main()
