from argparse import ArgumentParser

import forest_core
import forest_gui

# ------------------------------
# parser
# ------------------------------
parser = ArgumentParser(
    prog = 'forest',
    usage = 'usage',
    description = 'description',
    add_help = True)
parser.add_argument( '--cache-dir', required = False, default = 'cache', help = 'cache dir')
#parser.add_argument('-k', '--keywords', required = True, nargs = '*', help = 'keyword')
#parser.add_argument('-c', '--count', default = 1000, type = int, help = 'count')
#parser.add_argument('-r', '--rank', default = 100, type = int, help = 'rank')
#parser.add_argument('-y', '--year', default = 2019, type = int, help = 'year')
parser.add_argument('--mode', default = 'cui', choices = ['cui', 'gui'], help = 'mode')
args = parser.parse_args()

if args.mode == 'cui':
    print('mode: cui')
else:
    print('mode: gui')
    forest_gui.forest(
        cache_dir = args.cache_dir)
