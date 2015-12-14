import re
import subprocess
from collections import defaultdict, namedtuple
from .. import scannerbase


class Nomos(scannerbase.FileLicenseScanner):

    """Connector to FOSSology's 'nomos' license scanner."""

    name = 'nomos'
    Evidence = namedtuple('Evidence', ['license_name', 'position', 'length'])

    def __init__(self, conn, config):
        super(Nomos, self).__init__(conn, config)
        self.exec_path = config['scanner_' + Nomos.name + '_path']
        self.search_pattern = re.compile(r'License #(.*?)# at (.*?), length (.*?), index = .*?,')

    @staticmethod
    def _get_best_evidence(evidence_dict):
        return {
            name: max(evidence_dict[name], key=lambda x: int(x.length))
            for name in evidence_dict
            }

    @staticmethod
    def _get_extracted_text(file, evidence_info):
        try:
            with open(file.path, 'rb') as f:
                f.seek(int(evidence_info.position))
                extracted_text = f.read(int(evidence_info.length))
                return extracted_text
        except EnvironmentError:
            return ''

    def _get_licenses(self, file, nomos_output):
        parsed_output = [
            Nomos.Evidence(*item)
            for item in re.findall(self.search_pattern, nomos_output)
            ]
        all_evidence = defaultdict(list)
        for evidence_item in parsed_output:
            all_evidence[evidence_item.license_name].append(evidence_item)
        best_evidence = Nomos._get_best_evidence(all_evidence)
        license_list = {
            this_license: Nomos._get_extracted_text(file, best_evidence[this_license])
            for this_license in best_evidence
            }
        return license_list

    def process_file(self, file):
        args = (self.exec_path, '-S', file.path)
        output = subprocess.check_output(args)
        license_list = self._get_licenses(file, output)
        return license_list


scanner = Nomos
