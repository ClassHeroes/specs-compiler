import copy
import yaml
import os

__all__ = ['merge']


def merge(base_dir):
    prefixes = Prefixes()
    for urn, filename in file_yielder(base_dir):
        with filename.open() as file:
            data = yaml.load(file)

        if data['swagger'] != '2.0':
            raise ValueError('version 2.0 only')
        prefixes.register(urn, data)

    data = prefixes.render()
    return data


def file_yielder(base_dir):
    for pattern in ('**/*.yml', '**/*.yaml', '**/*.json'):
        for filename in base_dir.glob(pattern):
            if not filename.is_dir():
                yield str(filename.relative_to(base_dir)), filename


class Prefixes:
    def __init__(self):
        self.prefixes = {}
        self.data = {}

    def register(self, urn, data):
        if urn not in self.prefixes:
            parts = []
            for p in os.path.splitext(urn)[0].split('/'):
                r = [q.capitalize() for q in p.replace('-', '_').replace('.', '_').split('_')]
                parts.append(''.join(r))
            self.prefixes[urn] = '_'.join(parts)
        self.data[urn] = data

    def __getitem__(self, urn):
        prefix = self.prefixes[urn]
        data = self.data[urn]
        return prefix, data

    def __delitem__(self, urn):
        del self.prefixes[urn]
        del self.data[urn]

    def __iter__(self):
        for urn, prefix in self.prefixes.items():
            yield urn, (prefix, self.data[urn])

    def render(self):
        accumulated = {}
        sources = self.yield_rendered()
        accumulated = next(sources)
        descs = []
        consumes = []
        produces = []
        for data in sources:
            for key in ('paths', 'parameters', 'definitions'):
                accumulated[key].update(data[key])
            if data['info']['description']:
                descs.append(data['info']['description'].strip())
            if 'consumes' in data:
                consumes += data['consumes']
            if 'produces' in data:
                produces += data['produces']
        accumulated['info']['description'] = '\n\n'.join(descs)
        accumulated['consumes'] = list(set(consumes))
        accumulated['produces'] = list(set(produces))
        return accumulated

    def yield_rendered(self):
        ns = Namespace(self.prefixes)
        for urn, (prefix, data) in self:
            data = copy.deepcopy(data)
            data.setdefault('paths', {})
            data.setdefault('parameters', {})
            data.setdefault('definitions', {})
            data.setdefault('consumes', ['application/json'])
            data.setdefault('produces', ['application/json'])
            data = fix_definitions(urn, data, ns)
            data = fix_paths(data)
            data = fix_tags(urn, data)
            data = fix_refs(urn, data, ns)

            info = data.setdefault('info', {})
            desc = info.setdefault('description', '')
            if desc:
                data['info']['description'] = '# from %s:\n\n%s\n' % (urn, desc)
            yield data


def fix_refs(urn, data, prefixes):
    if isinstance(data, dict):
        if '$ref' in data:
            data['$ref'] = prefixes.ref(data['$ref'], urn)
        else:
            data = {key: fix_refs(urn, value, prefixes) for key, value in data.items()}
    elif isinstance(data, list):
        data = [fix_refs(urn, element, prefixes) for element in data]
    return data


def fix_definitions(urn, data, prefixes):
    objs = data.get('definitions', {})
    data['definitions'] = {}
    for key, value in objs.items():
        name = prefixes.definifion(key, urn)
        data['definitions'][name] = value
    return data


def fix_paths(data):
    base = data.get('basePath', '').rstrip('/')
    objs = data.get('paths', {})
    data['basePath'] = '/'
    data['paths'] = {}
    for key, value in objs.items():
        name = base + key
        data['paths'][name] = value
    return data


def fix_tags(urn, data):
    paths = data.setdefault('paths', {})
    tag = os.path.splitext(urn)[0]
    for path in paths.values():
        for k, v in path.items():
            if k in ('get', 'put', 'post', 'delete', 'options', 'head', 'patch'):
                alts = [tag]
                if tag.endswith('ies'):
                    alts.append('%sy' % tag[:-3])
                elif tag.endswith('s'):
                    alts.append('%s' % tag[:-1])
                elif tag.endswith('y'):
                    alts.append('%sies' % tag[:-1])
                else:
                    alts.append('%ss' % tag)

                tags = v.setdefault('tags', [])
                for a in alts:
                    if a in tags:
                        tags.remove(a)
                tags.append(tag)
    return data


class Namespace:
    def __init__(self, prefixes):
        self.prefixes = prefixes
        self.references = {}

    def __getitem__(self, urn):
        return self.prefixes[urn]

    def ref(self, pointer, doc):
        a, _, b = pointer.partition('#')

        if a == '':
            urn = doc
        else:
            urn = a
        if not b.startswith('/definitions/'):
            return pointer
        target = self.target(urn, b[13:])
        return '%s#/definitions/%s' % (a, target)

    def definifion(self, name, doc):
        target = self.target(doc, name)
        return target

    def target(self, urn, name):
        pref = self.prefixes[urn]
        return '%s_%s' % (pref, name)
