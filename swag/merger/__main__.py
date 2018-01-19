import argparse
import pathlib
from . import merge
from swag.formatters import format


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('dir')
    args = parser.parse_args(args)
    return args, parser


if __name__ == '__main__':
    args, parser = parse_args()
    base_dir = pathlib.Path(args.dir)
    if not base_dir.exists():
        raise ValueError('dir does not exists')
    if not base_dir.is_dir():
        raise ValueError('dir is not a dir')
    data = merge(base_dir)
    print(format(data))
