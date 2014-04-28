import i3


def get_current_output():
    ''' Returns the current output (the output with focus) '''
    workspaces = i3.msg('get_workspaces')
    workspace = i3.filter(tree=workspaces, focused=True)
    if workspace:
        return workspace[0]['output']
    else:
        return None


def get_current_workspace(mon='all'):
    ''' Returns the current workspace structure. '''
    workspaces = i3.msg('get_workspaces')
    if mon == 'all' or mon == get_current_output():
        return i3.filter(tree=workspaces, focused=True)
    else:
        return i3.filter(tree=workspaces, mon=mon, visible=True)


def get_windows_from_workspace(ws):
    ''' Returns all the window IDs for the specified workspace. '''
    res = []
    if ws is None:
        ws = get_current_workspace()[0]['name']
    workspace = i3.filter(name=ws)
    if workspace:
        workspace = workspace[0]
        windows = i3.filter(workspace, nodes=[])
        for window in windows:
            res.append(window['id'])
    return res
