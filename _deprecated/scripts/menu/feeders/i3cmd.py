#!/usr/bin/env python

# author: syl20bnr (2013)
# Feeder for i3ci_menu: Returns a list of i3 commands depending on prefix.


def get_prompt(prefix):
    p = "i3 command ->"
    if prefix:
        p = "i3 command ({0}) ->".format(prefix)
    return p


def feed(prefix):
    ''' Return a list of possible layout commands. '''
    if prefix == 'layout':
        return ['default',
                'splith',
                'splitv',
                'stacking',
                'tabbed',
                'toggle split']
    else:
        return ['reload', 'restart']


if __name__ == '__main__':
    print('\n'.join(feed()))
