import i3_utils
import common
import command


class used_workspaces(command.Command):
    ''' Output the names of all the currently used  workspaces. '''

    def init_parser(self, parser):
        common.add_monitor_param(parser)
        return self

    def validate_args(self, args):
        self._mon = common.get_monitor_value(args)
        return True

    def process(self):
        print i3_utils.get_current_workspaces(self._mon)
