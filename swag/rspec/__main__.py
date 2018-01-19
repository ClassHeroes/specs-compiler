import argparse
import pathlib
from . import rspec_compile_sources


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', nargs='+')
    parser.add_argument('--destination')
    args = parser.parse_args(args)
    return args, parser


def open_dir(source):
    path = pathlib.Path(source)
    if not path.exists():
        raise ValueError('dir does not exists')
    if not path.is_dir():
        raise ValueError('dir is not a dir')
    return path


if __name__ == '__main__':
    args, parser = parse_args()
    sources = [open_dir(source) for source in args.dir]
    destination = open_dir(args.destination)
    rspec_compile_sources(sources, destination)
