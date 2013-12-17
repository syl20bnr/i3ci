#!/usr/bin/env python

# author: syl20bnr (2013)
# Feeder for i3ci-menu: Returns to stdout the current focused window ID.

import i3


def get_prompt():
    return "Current window ID ->"


def get_current_window():
    windows = i3.filter(nodes=[])
    return i3.filter(tree=windows, focused=True)


def feed():
    ''' Returns the current window (the window with focus) '''
    window = get_current_window()
    if window:
        return window[0]['id']
    return ''


if __name__ == '__main__':
    print(feed())
