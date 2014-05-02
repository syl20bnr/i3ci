from abc import ABCMeta, abstractmethod
import sys
import inspect
import os
import re


class Command(object):
    ''' Base class for all i3ci commands.
    Note: The doc string of the commands derivated from this class
    are used as a description in the CLI.
    '''

    __metaclass__ = ABCMeta

    @abstractmethod
    def process(self):
        ''' Process the command. '''

    def init_parser(self, parser):
        ''' Declare command specific subparsers and arguments. '''
        return self

    def validate_args(self, args):
        ''' Validate the arguments and return True if the command
        can be executed. '''
        return True


class Category(Command):
    ''' A category contains commands.
    Note: The doc string of the commands derivated from this class
    are used as a description in the CLI.
    '''

    __metaclass__ = ABCMeta

    def __init__(self, module_name):
        self._mname = '.'.join(('i3ci.commands', module_name))
        self._cmds = {}

    def get_subcommands(self):
        mod = sys.modules[self._mname]
        classes = inspect.getmembers(
            mod, lambda x: inspect.isclass(x) and x.__module__ == self._mname)
        return [cls for name, cls in classes]

    def init_parser(self, parser):
        subparsers = parser.add_subparsers(
            title="Available commands",
            metavar='')
        self._cmds = self._add_commands(
            subparsers,
            [c() for c in self.get_subcommands()])

    def validate_args(self, args):
        self._sel = [x for x in self._cmds.keys() if x in sys.argv]
        if self._sel:
            return self._cmds[self._sel[0]].validate_args(args)
        else:
            return False

    def process(self):
        sel = [x for x in self._cmds.keys() if x in sys.argv]
        if not sel:
            print('Error: no action specified.')
        else:
            self._cmds[sel[0]].process()

    def _add_commands(self, subparsers, commands):
        ''' Add parsers (sub commands) to this command. '''
        cmds = {}
        for c in commands:
            n = c.__class__.__name__
            p = subparsers.add_parser(n, help=c.__doc__, description=c.__doc__)
            cmds[n] = c.init_parser(p)
        return cmds
