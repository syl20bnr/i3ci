import command
from current_output import current_output
from current_workspace import current_workspace
from workspace_name_catalog import workspace_name_catalog
from used_workspaces import used_workspaces
from free_workspaces import free_workspaces


class info(command.Category):
    ''' Get information. To get the list of the available commands type
    "i3ci_cmd info -h" '''

    def get_subcommands(self):
        return [current_output,
                current_workspace,
                used_workspaces,
                free_workspaces,
                workspace_name_catalog]
