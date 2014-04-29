from subprocess import Popen, PIPE

import command
import common
import i3_utils
import i3_action
import menu_utils


class start_application(command.Command):
    '''Start an application using i3ci_menu on the specified monitor. '''

    def init_parser(self, parser):
        common.add_monitor_param(parser)
        common.add_new_workspace_param(parser)
        parser.add_argument(
            '-a', '--application',
            type=str,
            default=None,
            required=False,
            help=('Specify the application to launch. '
                  'i3ci_menu will not be launched.'))
        return self

    def validate_args(self, args):
        self._mon = common.get_monitor_value(args)
        self._new = args.new
        self._app = args.application
        return True

    def process(self):
        reply = self._app
        if not reply:
            input_ = menu_utils.applications_feed()
            size = menu_utils.get_max_row(len(input_))
            proc = menu_utils.create_menu(lmax=size)
            reply = proc.communicate(input_)[0]
        if reply:
            cls = i3_action.Action
            reply = reply.decode('utf-8')
            if '-cd' in reply:
                # MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
                # # DMENU = os.path.normpath(os.path.join(MODULE_PATH,
                # # '../../bin/i3ci_menu'))
                xcwd = Popen('xcwd', stdin=PIPE, stdout=PIPE).communicate()[0]
                reply = '"' + reply + ' ' + xcwd + '"'
            if not self._new and (
                    self._mon == 'all' or
                    self._mon == i3_utils.get_current_output()):
                # open on the current workspace
                action = cls()
                action.add_action(cls.exec_, (reply,))
                i3_action.default_mode(action)
                action.process()
            if not self._new and (
                    self._mon != 'all' and
                    self._mon != i3_utils.get_current_output()):
                # open on the visible workspace on another output
                otherw = i3_utils.get_current_workspace(self._mon)
                action = cls()
                action.add_action(cls.jump_to_workspace, (otherw,))
                action.add_action(cls.exec_, (reply,))
                i3_action.default_mode(action)
                action.process()
            elif self._new and (
                    self._mon == 'all' or
                    self._mon == i3_utils.get_current_output()):
                # new workspace on the current output
                neww = i3_utils.get_free_workspaces()[0]
                action = cls()
                action.add_action(cls.jump_to_workspace, (neww,))
                action.add_action(cls.exec_, (reply,))
                i3_action.default_mode(action)
                action.process()
            elif self._new and (
                    self._mon != 'all' and
                    self._mon != i3_utils.get_current_output()):
                # new workspace on another output
                neww = i3_utils.get_free_workspaces()[0]
                action = cls()
                action.add_action(cls.focus_output, (self._mon,))
                action.add_action(cls.jump_to_workspace, (neww,))
                action.add_action(cls.exec_, (reply,))
                i3_action.default_mode(action)
                action.process()
        else:
            i3_action.default_mode()
