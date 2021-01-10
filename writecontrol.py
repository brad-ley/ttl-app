from pathlib import Path as P
import sys
import ast

if sys.argv[1] == 'bri':
    outdict = ast.literal_eval(P(__file__).parent.joinpath('commands.txt').read_text())
    outdict['bri'] = float(sys.argv[2])
    outdict['com'] = 'bri'
else:
    try:
        outdict = {
                'com':sys.argv[1],
                'on':float(sys.argv[2]),
                'off':float(sys.argv[3]),
                'rep':float(sys.argv[4]),
                'bri':float(sys.argv[5])
                }
    except IndexError:
        outdict = {
                'com':'error',
                'on':0,
                'off':0,
                'rep':0,
                'bri':100
                }

P(__file__).parent.joinpath('commands.txt').write_text(repr(outdict))
