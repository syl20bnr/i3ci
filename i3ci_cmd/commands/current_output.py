#!/usr/bin/env python
# Description:
# Returns the current workspace name.
import i3_utils
import command


class current_output(command.Command):
    ''' Output the name of the current output. '''

    def init_parser(self, parser):
        return self

    def validate_options(self, pargs):
        return True

    def process(self):
        ''' Returns the current output (the output with focus). '''
        print i3_utils.get_current_output()
