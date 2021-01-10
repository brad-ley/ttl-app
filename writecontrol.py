from pathlib import Path as P
import sys

try:
    outdict = {
            'com':sys.argv[1],
            'on':float(sys.argv[2]),
            'off':float(sys.argv[3]),
            'rep':float(sys.argv[4])
            }
except IndexError:
    outdict = {
            'com':'error',
            'on':0,
            'off':0,
            'rep':0
            }

P(__file__).parent.joinpath('commands.txt').write_text(repr(outdict))
