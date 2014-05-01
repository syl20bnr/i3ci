from commands import *


class focus_active_workspace(command.Command):
    ''' Focus the active workspace on the specified monitor. '''

    def init_parser(self, parser):
        common.add_monitor_param(parser)
        return self

    def validate_args(self, args):
        self._mon = common.get_monitor_value(args)
        return True

    def process(self):
        wks = i3_utils.get_current_workspace(self._mon)
        action = Action()
        action.add_action(Action.jump_to_workspace, (wks,))
        i3_action.default_mode(action)
        action.process()
