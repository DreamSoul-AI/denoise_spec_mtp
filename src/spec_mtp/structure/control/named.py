import yaml


class NamedDict(dict):
    """Dict subclass with attribute-style access."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' has no attribute '{key}'")

    def __setattr__(self, key, value):
        self[key] = _convert(value)

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)


def _convert(obj):
    if isinstance(obj, dict) and not isinstance(obj, NamedDict):
        return NamedDict({k: _convert(v) for k, v in obj.items()})
    if isinstance(obj, list):
        return [_convert(v) for v in obj]
    return obj


def get_config(path):
    with open(path, 'r') as f:
        raw = yaml.safe_load(f)
    cfg = _convert(raw)
    cfg['cfg_file'] = path
    return cfg


def apply_override(cfg, dotted_key, raw_value):
    """Apply a `--set a.b.c=value` style override with YAML-typed value."""
    keys = dotted_key.split('.')
    node = cfg
    for key in keys[:-1]:
        if key not in node or not isinstance(node[key], dict):
            node[key] = NamedDict()
        node = node[key]
    node[keys[-1]] = _convert(yaml.safe_load(raw_value))
