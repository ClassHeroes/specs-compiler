import argparse
import pathlib
from . import flatten
from swag.formatters import format


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args(args)
    return args, parser


if __name__ == '__main__':
    args, parser = parse_args()
    source = pathlib.Path(args.filename).resolve()
    if not source.exists():
        parser.error('file does not exists')
    if source.is_dir():
        parser.error('directory not allowed')
    data = flatten(source)
    print(format(data))
