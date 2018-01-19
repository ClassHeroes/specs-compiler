import yaml
import pathlib

__all__ = ['flatten']


def flatten(source):
    """Resolve every reference that are outside of file
    """
    if isinstance(source, pathlib.Path):
        base_dir = source.parent
    else:
        raise ValueError('cannot handle %s' % source.__class__.__name__)
    urn = str(source.relative_to(base_dir))
    registry = load_directory(base_dir)
    data = registry[urn]
    data = traverse_root(data, urn, registry)
    return data


def load_directory(base_dir):
    accumulator = {}
    for filename in yield_files(base_dir):
        name = str(filename.relative_to(base_dir))
        with filename.open() as file:
            data = yaml.load(file)
        accumulator[name] = data
    return accumulator


def yield_files(base_dir, patterns=('**/*.yaml', '**/*.json', '**/*.yml')):
    for pattern in patterns:
        for filename in base_dir.glob(pattern):
            if not filename.is_dir():
                yield filename


def traverse_root(obj, urn, registry=None):
    if isinstance(obj, dict):
        if '$ref' in obj:
            if not obj['$ref'].startswith('#/'):
                frag_urn, frag_obj = resolve_ref(obj['$ref'], registry)
                obj = frag_obj
        else:
            obj = {key: traverse_root(value, urn, registry) for key, value in obj.items()}
    elif isinstance(obj, list):
        obj = [traverse_root(element, urn, registry) for element in obj]
    return obj


def resolve_ref(ref, registry):
    urn, _, path = ref.partition('#')
    document = obj = registry[urn]
    if path == '/':
        pass
    elif path == '':
        obj = document['']
    elif path.startswith('/'):
        for key in path[1:].split('/'):
            obj = obj[key]
    else:
        raise ValueError('not a valid ref %s' % ref)

    return urn, traverse_ref(urn, obj, registry)


def traverse_ref(urn, obj, registry):
    if isinstance(obj, dict):
        if '$ref' in obj:
            a, _, b = obj['$ref'].partition('#')
            if a == '':
                a = urn
            else:
                a = pathlib.Path(urn).with_name(a)
                a = str(a)
            ref = '%s#%s' % (a, b)
            frag_urn, frag_obj = resolve_ref(ref, registry)
            obj = frag_obj
        else:
            obj = {key: traverse_ref(urn, value, registry) for key, value in obj.items()}
    elif isinstance(obj, list):
        obj = [traverse_ref(urn, element, registry) for element in obj]
    return obj
