import re
import subprocess
from itertools import izip
from .. import scannerbase

class Nomos(scannerbase.FileLicenseScanner):

    """Connector to FOSSology's 'nomos' license scanner."""

    name = 'nomos'

    def __init__(self, conn, config):
        super(Nomos, self).__init__(conn, config)
        self.exec_path = config['scanner_' + Nomos.name + '_path']
        self.search_pattern = re.compile(r'File (.+?) contains license\(s\) (.+)')
        self.lic_short_names_query_result = self.conn.execute("select short_name from licenses where is_spdx_official = 1")
        self.official_spdx_lic_short_name = []
        for row in self.lic_short_names_query_result:
            self.official_spdx_lic_short_name.append(str(row['short_name']).encode('ascii').strip(','))

    def process_file(self, file):
        # Nomos -S Switch - Ref:FOSSology documentation
        args = (self.exec_path, '-S', file.path)
        output = subprocess.check_output(args)
        # Return this to scanresult - Handle changes in scanresult.py
        scan_result = set()
        # Regex list goes here
        nomos_lic_match = re.compile(r'\#\w+')
        nomos_no_lic_match = re.compile(r'File (.+?) contains license\(s\) No_license_found (.+)')
        nomos_fil_name_pattern = re.search('File (.+?) contains', output)
        # Variables - Function local
        ## Extraction variables
        counter = 0 # Counter init -
        file_lics = []
        lic_start_pos = []
        lic_end_pos = []
        ## Return these variables with scan_result
        extracted_text = []
        file_name = nomos_fil_name_pattern.group(0).strip('File').strip('contains').strip(' ')


        if re.match(nomos_no_lic_match, output):
            #print(output)
            file_lics = 'No_license_found'
            extracted_text = ''
        else:
            output_list = re.split(r'\s*',output)
            for item in output_list:
                counter+=1
                # Use counter to determin the license found for the file, start and end position for license text
                if re.match(nomos_lic_match, item):
                    file_lics.append(output_list[counter-1].strip('#'))
                    lic_start_pos.append(int(output_list[counter+1].strip(',')))
                    lic_end_pos.append(int(output_list[counter+1].strip(','))+ int(output_list[counter+3].strip(',')))
            counter = 0 # Reset counter - Regardless of initialization
        # Read file characters - for extracted text
        file_chars = []
        with open(file.path, 'r') as fileread:
            for line in fileread:
                for char in line:
                    file_chars.append(char)
        # Official SPDX license - comparision by short_name - Ref:SPDX db schema
        for off_lic in self.official_spdx_lic_short_name:
            for found_lic, start_pos, end_pos in izip(file_lics, lic_start_pos, lic_end_pos):
                if found_lic != off_lic:
                    extracted_text.append(''.join(file_chars[start_pos:end_pos]))
                else:
                    extracted_text.append('')
        scan_result = file_name, zip(file_lics, extracted_text)
        return scan_result
                             

scanner = Nomos
