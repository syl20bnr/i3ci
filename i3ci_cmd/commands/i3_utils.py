import string
import i3


# Outputs
# -----------------------------------------------------------------------------

def get_outputs_dictionary():
    ''' Returns a dictionary where key is a natural output name
    like "monitor 1" and value is the low level name like
    "xinerama-0"'''
    res = {}
    outputs = i3.msg('get_outputs')
    for i, o in enumerate(outputs):
        res['monitor {0}'.format(i+1)] = o['name']
    return res


def get_current_output():
    ''' Returns the current output (the output with focus) '''
    workspaces = i3.msg('get_workspaces')
    workspace = i3.filter(tree=workspaces, focused=True)
    if workspace:
        return workspace[0]['output']
    else:
        return None


# Workspaces
# -----------------------------------------------------------------------------

def get_workspace_name_catalog():
    ''' Returns a raw list of all possible workspace names formed
    with one char. '''
    return ([str(x) for x in range(0, 10)] +
            [x for x in string.lowercase] +
            ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-',
             '_', '=', '+', '[', '{', ']', '}', '|', '\\', ';', ':',
             "'", '"', '.', '<', '>', '/', '?', '~', '`'])


def get_workspaces(mon='all'):
    ''' Returns a structure containing all the opened workspaces. '''
    used = []
    ws_tree = i3.msg('get_workspaces')
    outs = get_outputs_dictionary()
    for o in outs.itervalues():
        if mon == 'all' or mon == o:
            for ws in get_workspace_name_catalog():
                if i3.filter(tree=ws_tree, output=o, name=ws):
                    used.append(ws)
    used.append('`')
    return sorted(used)


def get_current_workspace(mon='all'):
    ''' Returns the current workspace structure. '''
    workspaces = i3.msg('get_workspaces')
    if mon == 'all' or mon == get_current_output():
        return i3.filter(tree=workspaces, focused=True)[0]['name']
    else:
        return i3.filter(tree=workspaces, output=mon, visible=True)[0]['name']


def get_current_workspaces(mon='all'):
    ''' Returns a list of the names of all currently used workspaces on the
    specified output. '''
    all_ws = get_workspace_name_catalog()
    used = []
    ws_tree = i3.msg('get_workspaces')
    outs = get_outputs_dictionary()
    for o in outs.itervalues():
        if mon == 'all' or mon == o:
            for ws in all_ws:
                if i3.filter(tree=ws_tree, output=o, name=ws):
                    used.append(ws)
    return sorted(used)


def get_free_workspaces():
    ''' Returns the free workspace names '''
    res = []
    all_workspaces = get_workspace_name_catalog()
    used_workspaces = i3.msg('get_workspaces')
    for w in all_workspaces:
        if not i3.filter(tree=used_workspaces, name=w):
            res.append(w)
    return res


# Windows
# -----------------------------------------------------------------------------

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