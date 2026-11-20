import os

import yaml


# Get Valid Path
def find_valid_path(path, cwd=None):
    abspath = path
    if cwd:
        relpath = os.path.join(cwd, path)
    else:
        relpath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), path)
    if not os.path.isfile(abspath) and not os.path.isfile(relpath):
        return None
    if os.path.isfile(abspath):
        path = abspath
    elif os.path.isfile(relpath):
        path = relpath
    return path


def read_yaml(path: str) -> dict:
    orig = path
    # Check YAML Path
    try:
        path = find_valid_path(path, os.getcwd())
        assert path, f'YAML file "{orig}" could not be found'
    except FileNotFoundError:
        raise AssertionError(
            f'YAML file "{orig}" could not be found')
    # Check YAML can be Opened
    try:
        config = yaml.load(open(path), Loader=yaml.SafeLoader)
    except yaml.scanner.ScannerError:
        raise AssertionError(
            f'YAML file "{orig}" is not well formed')
    except yaml.constructor.ConstructorError:
        raise AssertionError(
            f'YAML file "{orig}" is attempting to create unsafe objects')
    # Check contents are a Dictionary
    assert isinstance(config, dict), (
        f'YAML file "{orig}" is not a dictionary')
    return config


def write_yaml(path: str, config: dict) -> None:
    yaml_file = open(path, 'w+')
    yaml.Dumper.ignore_aliases = lambda *args: True
    yaml.dump(
        config,
        yaml_file,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )
