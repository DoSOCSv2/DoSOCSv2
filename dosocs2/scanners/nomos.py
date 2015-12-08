import re
import subprocess
from itertools import izip
from collections import defaultdict
from sqlalchemy.sql import select
from .. import scannerbase
from .. import schema

class Nomos(scannerbase.FileLicenseScanner):

    """Connector to FOSSology's 'nomos' license scanner."""

    name = 'nomos'

    def __init__(self, conn, config):
        super(Nomos, self).__init__(conn, config)
        self.exec_path = config['scanner_' + Nomos.name + '_path']
        self.search_pattern = re.compile(r'File (.+?) contains license\(s\) (.+)')
        lics = schema.licenses.alias()
        official_licenses_query = select([lics.c.short_name]).where(lics.c.is_spdx_official == True)
        self.lic_short_names_query_result = self.conn.execute(official_licenses_query)
        self.official_spdx_lic_short_name = []
        for row in self.lic_short_names_query_result:
            self.official_spdx_lic_short_name.append(str(row['short_name']).encode('ascii').strip(','))

    def process_file(self, file):
        # Nomos -S Switch - Ref:FOSSology documentation
        args = (self.exec_path, '-S', file.path)
        output = subprocess.check_output(args)
        output_parse = re.findall(r'License #(.*?)# at (.*?), length (.*?), index = .*?,', output)
        licenses_list = defaultdict(list)
        for output_item in output_parse:
            licenses_list[output_item[0]].append(output_item)
        for key in licenses_list:
            licenses_list[key] = max(licenses_list[key], key=lambda x: int(x[2]))
            licenses_list[key] = list(licenses_list[key])
            if key not in self.official_spdx_lic_short_name:
                with open(file.path, 'rb') as current_file:
                    current_file.seek(int(licenses_list[key][1]))
                    licenses_list[key].append(current_file.read(int(licenses_list[key][2])))
            else:
               licenses_list[key].append('')
        return licenses_list      
scanner = Nomos
