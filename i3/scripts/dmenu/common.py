# author: syl20bnr (2013)
# Common functions for all feeders.

import re


# declare ---------------------------------------------------------------------


def add_monitor_param(parser, mandatory=False):
    parser.add_argument('-m', '--monitor',
                        type=int,
                        choices=[0, 1],
                        default=-1,
                        required=mandatory,
                        help='Monitor index, 0 for main and 1 for second.')


def add_free_param(parser, mandatory=False):
    parser.add_argument('-f', '--free',
                        action='store_true',
                        default=False,
                        required=mandatory,
                        help=('If true the action is performed on a free '
                              'workspace.'))


# retrieve --------------------------------------------------------------------


def get_monitor_value(args):
    mon = 'all'
    if args.monitor != -1:
        mon = 'xinerama-{0}'.format(args.monitor)
    return mon


def get_natural_monitor_value(output):
    mon = output
    index = get_output_index(output)
    if index:
        mon = 'monitor {0}'.format(index + 1)
    return mon


def get_output_index(output):
    m = re.match('^xinerama-([0-9]+)$', output)
    if m:
        return int(m.group(1))
    return None
