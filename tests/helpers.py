from contextlib import contextmanager
from dosocs2 import dosocs2, configtools
from tempfile import NamedTemporaryFile

@contextmanager
def TempEnv(config_text):
    with NamedTemporaryFile(mode='w+') as temp_config:
        with NamedTemporaryFile(mode='w+') as temp_db:
            temp_config.write(config_text.format(temp_db.name))
            temp_config.flush()
            args = [
                'dbinit', 
                '-f',
                temp_config.name,
                '--no-confirm'
                ]
            ret = run_dosocs2(args)
            yield temp_config, temp_db


def run_dosocs2(args):
    return dosocs2.main(args)
