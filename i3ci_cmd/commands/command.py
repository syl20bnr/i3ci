from abc import ABCMeta, abstractmethod
import sys
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

    # @abstractmethod
    # def get_subcommands(self):
    #     ''' Returns a list of command classes. '''

    def __init__(self):
        self._cmds = {}

    def get_subcommands(self):
        # programmatically load all the subcommands
        catpkg = "_{0}".format(self.__class__.__name__)
        moddir = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(moddir, 'categories', catpkg)
        cmdnames = [f.replace('.py', '') for f in os.listdir(path)
                    if re.match('.*py$', f) and 'init' not in f]
        cmds = []
        for cmdname in cmdnames:
            relmodpath = 'categories.{0}.{1}'.format(catpkg, cmdname)
            t = __import__(relmodpath, globals(), locals(), [cmdname], -1)
            globals()[cmdname] = t.__dict__[cmdname]
            cmds.append(t.__dict__[cmdname])
        return cmds

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
