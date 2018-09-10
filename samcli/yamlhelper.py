"""
Helper to be able to parse/dump YAML files
"""

import json

import yaml


def yaml_dump(dict_to_dump):
    """
    Dumps the dictionary as a YAML document
    :param dict_to_dump:
    :return:
    """
    return yaml.safe_dump(dict_to_dump, default_flow_style=False)


def yaml_parse(yamlstr):
    """Parse a yaml string"""
    try:
        # PyYAML doesn't support json as well as it should, so if the input
        # is actually just json it is better to parse it with the standard
        # json parser.
        return json.loads(yamlstr)
    except ValueError:
        return yaml.safe_load(yamlstr)
