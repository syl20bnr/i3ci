import command
import common
import i3_utils
import i3_action


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
        cls = i3_action.Action
        action = cls()
        action.add_action(cls.jump_to_workspace, (wks,))
        i3_action.default_mode(action)
        action.process()
