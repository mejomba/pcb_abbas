import argparse
import os

parser = argparse.ArgumentParser()

parser.add_argument('-d', help='path to directory')
parser.add_argument('-f', help='path to file')
parser.add_argument('-F', help='file extension')

args = parser.parse_args()

d = args.d
f = args.f
F = args.F


def get_size(d, switch):
    size = 0
    if switch == 'd':
        for current_path, directories, files in os.walk(d):
            for file in files:
                PATH = os.path.join(current_path, file)
                size += os.path.getsize(PATH)
        return f'{size / 1000} kb'

    elif switch == 'f':
        return f'{os.path.getsize(d) / 1000} kb'

    elif switch == 'Fd':
        for current_path, directories, files in os.walk(d):
            for file in files:
                PATH = os.path.join(current_path, file)
                if os.path.splitext(PATH)[1][1:] == args.F:
                    size += os.path.getsize(PATH)
        return f'{size / 1000} kb'


if d and f:
    print('-d and -f not allowed')
elif d and not f and not F:
    if not os.path.isdir(d):
        print(f'{d} not a directory')
    else:
        print(get_size(d, switch='d'))
elif f and not d and not F:
    if not os.path.isfile(f):
        print(f'{f} not a file')
    else:
        print(get_size(f, switch='f'))
elif F and d and not f:
    if os.path.isdir(d):
        print(get_size(d, switch='Fd'))
    else:
        print(f'{d} not a directory')
elif F and f and not d:
    if os.path.isfile(f):
        print(get_size(f, switch='f'))
    else:
        print(f'{f} not a file')
else:
    print('file or directory not specified')

