#!/usr/bin/env python

# author: syl20bnr (2013)
# Feeder for i3ci_menu: Returns free workspaces.

import i3

import workspaces


def get_prompt(verb):
    return "{0} workspace ->".format(verb)


def get_free_workspaces():
    ''' Returns the free workspaces (the workspace with focus) '''
    res = []
    all_workspaces = workspaces.get_workspaces_no_prefix()
    used_workspaces = i3.msg('get_workspaces')
    for w in all_workspaces:
        if not i3.filter(tree=used_workspaces, name=w):
            res.append(w)
    return res


def feed():
    ''' Returns the free workspaces (the workspace with focus) '''
    return get_free_workspaces()


if __name__ == '__main__':
    print(feed())
