'''
 Commands requiring the i3ci menu. To get the list of possible
action type "i3ci_cmd menu -h"
 '''
from subprocess import Popen, PIPE

from i3ci import *


class start_application(command.Command):
    '''Start an application using i3ci_menu on the specified monitor. '''

    def init_parser(self, parser):
        params.add_monitor_param(parser)
        params.add_new_workspace_param(parser)
        parser.add_argument(
            '-a', '--application',
            type=str,
            default=None,
            required=False,
            help=('Specify the application to launch. '
                  'i3ci_menu will not be launched.'))
        return self

    def validate_args(self, args):
        self._mon = params.get_monitor_value(args)
        self._new = args.new
        self._app = args.application
        return True

    def process(self):
        reply = self._app
        if not reply:
            input_ = utils.applications_feed()
            size = utils.get_max_row(len(input_))
            proc = utils.create_menu(lmax=size)
            reply = proc.communicate(input_)[0]
        if reply:
            reply = reply.decode('utf-8')
            if '-cd' in reply:
                # MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
                # DMENU = os.path.normpath(os.path.join(MODULE_PATH,
                # '../../bin/i3ci_menu'))
                xcwd = Popen('xcwd', stdin=PIPE, stdout=PIPE).communicate()[0]
                reply = '"' + reply + ' ' + xcwd + '"'
            if not self._new and (
                    self._mon == 'all' or
                    self._mon == utils.get_current_output()):
                # open on the current workspace
                a = action.Action()
                a.add(action.Action.exec_, (reply,))
                action.default_mode(a)
                a.process()
            if not self._new and (
                    self._mon != 'all' and
                    self._mon != utils.get_current_output()):
                # open on the visible workspace on another output
                otherw = utils.get_current_workspace(self._mon)
                a = action.Action()
                a.add(action.Action.jump_to_workspace, (otherw,))
                a.add(action.Action.exec_, (reply,))
                action.default_mode(a)
                a.process()
            elif self._new and (
                    self._mon == 'all' or
                    self._mon == utils.get_current_output()):
                # new workspace on the current output
                neww = utils.get_free_workspaces()[0]
                a = action.Action()
                a.add(action.Action.jump_to_workspace, (neww,))
                a.add(action.Action.exec_, (reply,))
                action.default_mode(a)
                a.process()
            elif self._new and (
                    self._mon != 'all' and
                    self._mon != utils.get_current_output()):
                # new workspace on another output
                neww = utils.get_free_workspaces()[0]
                a = action.Action()
                a.add(action.Action.focus_output, (self._mon,))
                a.add(action.Action.jump_to_workspace, (neww,))
                a.add(action.Action.exec_, (reply,))
                action.default_mode(a)
                a.process()
        else:
            action.default_mode()
