from argparse import ArgumentParser

import forest_cui
import forest_gui

parser = ArgumentParser(
    prog = 'forest',
    usage = 'usage',
    description = 'description',
    add_help = True)
parser.add_argument(
    '--output-dir',
    required = False,
    default = 'cache',
    help = 'output dir')
parser.add_argument('--input-dir', required = False, help = 'input dir')
parser.add_argument('-k', '--keywords', required = True, nargs = '*', help = 'keyword')
parser.add_argument('-c', '--count', default = 1000, type = int, help = 'count')
parser.add_argument('-r', '--rank', default = 100, type = int, help = 'rank')
parser.add_argument('-t', '--tier', default = 1, type = int, help = 'tier')
parser.add_argument('--mode', default = 'cui', choices = ['cui', 'gui'], help = 'tier')
args = parser.parse_args()

if args.mode == 'cui':
    print('mode: cui')
    forest_cui.forest(args.keywords, args.count, args.rank, args.tier, args.output_dir, args.input_dir)
else:
    print('mode: gui')
    forest_gui.forest(args.keywords, args.count, args.rank, args.tier, args.output_dir, args.input_dir)
