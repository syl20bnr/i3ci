#!/usr/bin/env python

# author: syl20bnr (2013)
# Feeder for i3ci-menu: Returns to stdout the list of all possible workspaces

import string


def get_prompt(verb):
    return "{0} workspace ->".format(verb)


def get_workspaces_no_prefix():
    ''' Return a raw list of all possible workspaces formed with one char.
    The '`' workspace means back_and_forth command instead of a workspace.
    '''
    return ([str(x) for x in range(0, 10)] +
            [x for x in string.lowercase] +
            ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-',
             '_', '=', '+', '[', '{', ']', '}', '|', '\\', ';', ':',
             "'", '"', '.', '<', '>', '/', '?', '~', '`'])


def feed():
    ''' Return a list of all possible workspaces formed with one char. '''
    workspaces = get_workspaces_no_prefix()
    return workspaces

if __name__ == '__main__':
    print('\n'.join(feed()))
