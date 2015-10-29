import re
import subprocess

from .. import scannerbase

class Nomos(scannerbase.FileLicenseScanner):

    """Connector to FOSSology's 'nomos' license scanner."""

    name = 'nomos'

    def __init__(self, conn, config):
        super(Nomos, self).__init__(conn, config)
        self.exec_path = config['scanner_' + Nomos.name + '_path']
        self.search_pattern = re.compile(r'File (.+?) contains license\(s\) (.+)')

    def process_file(self, file):
        args = (self.exec_path, '-l', file.path)
        output = subprocess.check_output(args)
        scan_result = set()
        for line in output.split('\n'):
            m = re.match(self.search_pattern, line)
            if m is None:
                continue
            scan_result.update({
                lic_name
                for lic_name in m.group(2).split(',')
                if lic_name != 'No_license_found'
                })
        return scan_result

scanner = Nomos
