#!/usr/bin/env python
# Description:
# Returns the current workspace name.
import common
import i3_utils
import command


class current_workspace(command.Command):
    ''' Output the name of the current workspace. '''

    def init_parser(self, parser):
        common.add_monitor_param(
            parser,
            add_description=('An empty string is returned if the specified '
                             'monitor does not contain the current '
                             'workspace'))
        return self

    def validate_options(self, pargs):
        self._mon = common.get_monitor_value(pargs)
        return True

    def process(self):
        ''' Returns the current workspace on the specified output '''
        workspace = i3_utils.get_current_workspace(self._mon)
        if workspace:
            print workspace[0]['name']
        else:
            print ''
