from subprocess import Popen, PIPE


I3CI_MENU_MAX_ROW = 32
I3CI_MENU_HEIGHT = 18
I3CI_MENU_FONT = 'Ubuntu Mono-9:normal'


def create_menu(p=None,
                a=100,
                f=I3CI_MENU_FONT,
                lmax=8,
                lv=True,
                m=-1,
                h=I3CI_MENU_HEIGHT,
                r=False,
                nb='#002b36',
                nf='#657b83',
                sb='#859900',
                sf='#eee8d5'):
    ''' Returns a i3ci_menu process with the specified title and number
    of rows. '''
    cmd = ['i3ci_menu', '-f', '-i', '-lmax', str(lmax), '-y', '19',
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
    return Popen(cmd, stdin=PIPE, stdout=PIPE)


def applications_feed():
    ''' Returns a list of all found executables under paths. '''
    p = Popen('dmenu_path', stdout=PIPE, stderr=PIPE, shell=True)
    return p.stdout.read().encode('utf-8')


def get_max_row(rcount):
    return max([0, min([I3CI_MENU_MAX_ROW, rcount])])
