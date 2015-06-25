from ConfigParser import RawConfigParser
import pkg_resources
import os
import shutil

DEFAULT_CONFIG_PATH = pkg_resources.resource_filename('dosocs2', 'default/dosocs2.conf')
XDG_CONFIG_HOME = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
DOSOCS2_CONFIG_HOME = os.path.join(XDG_CONFIG_HOME, 'dosocs2')
DOSOCS2_CONFIG_PATH = os.path.join(DOSOCS2_CONFIG_HOME, 'dosocs2.conf')


def create_user_config(overwrite=True):
    try:
        os.makedirs(DOSOCS2_CONFIG_HOME)
    except (OSError, IOError, EnvironmentError):
        pass
    try:
        if overwrite or not os.path.exists(DOSOCS2_CONFIG_PATH):
            shutil.copyfile(DEFAULT_CONFIG_PATH, DOSOCS2_CONFIG_PATH)
    except (OSError, IOError, EnvironmentError):
        return False
    return True


def update_config(other_config_path=None):
    global config
    global connection_uri
    global namespace_prefix
    _parser = RawConfigParser()
    _parser.read([DEFAULT_CONFIG_PATH, other_config_path or DOSOCS2_CONFIG_PATH])
    config = {section: dict(_parser.items(section))
              for section in _parser.sections()
              }
    uri_fmt = '{dbms}://{user}:{password}@{host}:{port}/{database}'
    connection_uri = uri_fmt.format(**config['database'])
    prefix_fmt = '{dbms}://{host}:{port}/{database}'
    namespace_prefix = prefix_fmt.format(**config['database'])

update_config()
