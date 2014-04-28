from abc import ABCMeta, abstractmethod


class Command(object):
    ''' Base class for all i3ci commands.
    Note: The doc strings of the derivated classes are help
    messages displayed when the -h parameter is provided on the
    command line.
    '''

    __metaclass__ = ABCMeta

    @abstractmethod
    def init_parser(self, parser):
        '''
        Declare command specific subpargers and arguments.
        '''

    @abstractmethod
    def validate_options(self, pargs):
        '''
        '''
        return True

    @abstractmethod
    def process(self):
        '''
        Process the command.
        '''

    def add_parsers(self, subparsers, commands):
        '''
        Add parsers (sub commands) to this command.
        '''
        cmds = {}
        for c in commands:
            n = c.__class__.__name__
            p = subparsers.add_parser(n, help=c.help())
            cmds[n] = c.init_parser(p)
        return cmds

    def help(self):
        '''
        The help for this command.
        '''
        return ''
