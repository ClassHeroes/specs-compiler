import yaml
import json
import sys

__all__ = ['format', 'Dumper']


class Dumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        """Indent block sequence by 2
        """
        return super().increase_indent(flow, False)


def represent_dict(dumper, data):
    """Keeps keys ordered
    """
    return dumper.represent_mapping('tag:yaml.org,2002:map', data.items(), flow_style=False)

def represent_list(dumper, data):
    """Keeps sequence in colums
    """
    return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=False)

def represent_stringish(dumper, data):
    """Fold string with > or |
    """
    style = None

    """ format JSON
    """
    try:
        clean_data = data.strip()
        if (clean_data[0] in '{['):
            loaded_data = json.loads(data)
            style='|'
            return yaml.representer.ScalarNode('tag:yaml.org,2002:str', json.dumps(loaded_data, indent=2), style=style)
    except:
        pass

    if '\n' in data.strip('\n'):
        style = '|'
    elif '\n' in data or not data or data == '-' or data[0] in '!&*[':
        style = 'literal'
        if '\n' in data[:-1]:
            for line in data.splitlines():
                if len(line) > dumper.best_width:
                    break
            else:
                style = '|'

        elif data and data[-1] == '\n':
            style = '>'
    return yaml.representer.ScalarNode('tag:yaml.org,2002:str', data, style=style)

Dumper.add_representer(list, represent_list)
Dumper.add_representer(dict, represent_dict)
Dumper.add_representer(str, represent_stringish)


def format(document):
    return yaml.dump(document, Dumper=Dumper, indent=2)
