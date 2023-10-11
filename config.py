import os
import sys
from functools import lru_cache

import yaml

CONFIG_FILE_NAME = "config.yaml"


def _get_config_path():
    return os.path.join(os.path.dirname(os.path.abspath(sys.modules["__main__"].__file__)), CONFIG_FILE_NAME)


@lru_cache(maxsize=1)
def get_config():
    with open(_get_config_path(), "r") as yamlf:
        try:
            return yaml.safe_load(yamlf)
        except yaml.YAMLError as exc:
            print("Error while parsing {}:".format(CONFIG_FILE_NAME))
            print(exc)
            sys.exit()
