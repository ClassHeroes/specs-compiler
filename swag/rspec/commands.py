from swag.utils import log, camel2snake
import hashlib
import json
import yaml
import os.path

__all__ = ['rspec_compile_sources']


def rspec_compile_sources(sources, destination):
    for source in sources:
        for s in source.glob('**/*.yml'):
            urn = str(s.relative_to(source.parent))
            rspec_compile(urn, s, destination)
        for s in source.glob('**/*.yaml'):
            urn = str(s.relative_to(source.parent))
            rspec_compile(urn, s, destination)
        for s in source.glob('**/*.json'):
            urn = str(s.relative_to(source.parent))
            rspec_compile(urn, s, destination)


def rspec_compile(urn, source, destination):
    with source.open() as file:
        data = yaml.load(file)
    if data['swagger'] != '2.0':
        raise ValueError('swagger 2.0 only')
    definitions = data.get('definitions', {})
    for name, operations in data['paths'].items():
        dest_dir = destination / os.path.splitext(urn)[0]
        os.makedirs(dest_dir, exist_ok=True)
        digest = hashlib.md5(str(source).encode('utf-8')).hexdigest()
        for op_name in ('get', 'post', 'put', 'patch', 'delete'):
            if op_name in operations:
                op = operations[op_name]
                op_id = op.get('operationId', '%s_%s' % (digest, op_name))
                output_file = dest_dir / ('%s.json' % camel2snake(op_id))
                responses = op['responses']
                for code in (200, 201, '200', '201'):
                    if code in responses:
                        output_file = dest_dir / ('%s_2xx.json' % camel2snake(op_id))
                        log('generate', output_file)
                        schema = responses[code]['schema']
                        # TODO resolve dependencies
                        while '$ref' in schema:
                            ref = schema['$ref']
                            if ref.startswith('#/definitions/'):
                                def_name = ref[14:]
                                schema = definitions[def_name]
                        schema = traverse(schema, schema, definitions)
                        with output_file.open(mode='w') as file:
                            json.dump(schema, file, indent=2)
                        break
                for code in responses.keys():
                    if code in (200, 201, '200', '201'):
                        continue
                    elif 'schema' not in responses[code]:
                        continue
                    schema = responses[code]['schema']
                    output_file = dest_dir / ('%s_%s.json' % (camel2snake(op_id), code))
                    log('generate', output_file)
                    # TODO resolve dependencies
                    while '$ref' in schema:
                        ref = schema['$ref']
                        if ref.startswith('#/definitions/'):
                            def_name = ref[14:]
                            schema = definitions[def_name]
                    schema = traverse(schema, schema, definitions)
                    with output_file.open(mode='w') as file:
                        json.dump(schema, file, indent=2)


def traverse(schema, root, definitions):
    if isinstance(schema, dict):
        if '$ref' in schema:
            ref = schema['$ref']
            if ref.startswith('#/definitions/'):
                def_name = ref[14:]
                def_schema = definitions[def_name]
                root.setdefault('definitions', {})[def_name] = def_schema
                traverse(def_schema, root, definitions)
            else:
                raise NotImplementedError
        else:
            for member in list(schema.values()):
                traverse(member, root, definitions)
    elif isinstance(schema, list):
        for elt in schema:
            traverse(elt, root, definitions)
    return root
