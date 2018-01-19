import re
import sys

__all__ = ['log', 'camel2snake']


def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def camel2snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
