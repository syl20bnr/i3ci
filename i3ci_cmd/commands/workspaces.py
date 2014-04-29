import common
import i3_utils
import command
from i3_action import Action


class workspaces(command.Command):
    ''' Return a list of all currently opened workspaces. '''

    def init_parser(self, parser):
        common.add_monitor_param(
            parser,
            add_description=('An empty string is returned if the specified '
                             'monitor does not contain the current '
                             'workspace'))
        return self

    def validate_args(self, args):
        self._mon = common.get_monitor_value(args)
        return True

    def process(self):
        wks = cur_workspace.feed(mon)
        action = Action()
        action.add_action(Action.jump_to_workspace, (wks,))
        default_mode(action)
        action.process()
