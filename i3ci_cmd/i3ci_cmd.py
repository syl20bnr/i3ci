# -*- mode: python coding: utf-8 -*-
# Description:
# i3ci command line tool.
import sys
import os
import inspect
import argparse


# Constants
# ----------------------------------------------------------------------------

MODULE_NAME = os.path.splitext(os.path.basename(__file__))[0]
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
I3CI_CMD_PROG_NAME = MODULE_NAME
I3CI_CMD_HOME_DIR = '.i3ci'
I3CI_CMD_HOME = os.path.join(os.path.expanduser("~"), I3CI_CMD_HOME_DIR)


# Main
# ----------------------------------------------------------------------------

def main():
    try:
        init_include_dirs()
        args = None
        parser = init_parser()
        cmds = init_subparsers(parser)
        args = parser.parse_args()
        cmd = get_selected_cmd(cmds)
        if not cmd.validate_args(args):
            exit(1)
        cmd.process()
    except Exception:
        print('An error happened!')
        if not args or args.debug:
            print_traceback()
        exit(1)


# Implementation
# ----------------------------------------------------------------------------

def init_include_dirs():
    sys.path.append(os.path.join(SCRIPT_PATH, 'lib'))


def init_parser():
    parser = argparse.ArgumentParser(
        prog=I3CI_CMD_PROG_NAME,
        version='%(prog)s version ' + '0.1',
        description=('i3 config improved Command Line Interface.'),
        epilog=('Support: sylvain.benner@gmail.com'))
    parser.add_argument(
        '--debug',
        action='store_true',
        help=('display the call stack if an exception is '
              'raised.'))
    return parser


def init_subparsers(parser):
    import commands.categories
    cmd_modules = {}
    mod_all_cmds = sys.modules['commands.categories']
    classes = inspect.getmembers(mod_all_cmds, inspect.isclass)
    subparsers = parser.add_subparsers(
        title='Command categories',
        metavar='')
    for c in classes:
        c_inst = c[1]()
        cmd_modules[c[0]] = c_inst
        parser = subparsers.add_parser(
            c[0], help=c_inst.__doc__, description=c_inst.__doc__)
        c_inst.init_parser(parser)
    return cmd_modules


def get_selected_cmd(modules):
    sel = [x for x in modules.keys() if x in sys.argv]
    if not sel:
        print('Error: no command specified.')
        return None
    else:
        return modules[sel[0]]


def print_error(msg):
    print('Error: {0}'.format(msg))


def print_traceback():
    import traceback
    print traceback.format_exc()
