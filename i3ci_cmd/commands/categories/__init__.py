import os
import re

path = os.path.dirname(os.path.realpath(__file__))
cats = [f.replace('.py', '') for f in os.listdir(path)
        if re.match('.*py$', f) and 'init' not in f and 'info' not in f and 'do' not in f]
for c in cats:
    pkg = '.'.join(['commands.categories', c])
    t = __import__(pkg, globals(), locals(), [c], -1)
    globals()[c] = t.__dict__[c]
