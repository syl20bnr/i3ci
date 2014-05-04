# author: syl20bnr (2013)
# goal: Create a i3ci_menu process.

import os
from subprocess import Popen, PIPE

MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
MENU = os.path.normpath(os.path.join(MODULE_PATH, '../../bin/i3ci_menu'))


def call(p=None,
         a=100,
         f='fixed',
         lmax=8,
         lv=True,
         m=-1,
         h=16,
         r=False,
         nb='#002b36',
         nf='#657b83',
         sb='#859900',
         sf='#eee8d5'):
    ''' Returns a i3ci_menu process with the specified title and number
    of rows.
    '''
    cmd = [MENU, '-f', '-i', '-lmax', str(lmax), '-y', '19',
           '-fn', f, '-nb', nb, '-nf', nf, '-sb', sb, '-sf', sf]
    if p:
        cmd.extend(['-p', p])
    if h:
        cmd.extend(['-h', str(h)])
    if r:
        cmd.append('-r')
    if lv:
        cmd.append('-lv')
    if a != 0:
        cmd.extend(['-a', str(a)])
    if m is not None and m != 'all' and m != -1:
        cmd.extend(['-m', str(m)])
    # print cmd
    i3ci_menu = Popen(cmd, stdin=PIPE, stdout=PIPE)
    return i3ci_menu
