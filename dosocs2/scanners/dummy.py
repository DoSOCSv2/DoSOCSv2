from .. import scannerbase


class Dummy(scannerbase.Scanner):
    """No-op scanner."""

    name = 'dummy'

    def process_file(self, file):
        pass

    def store_results(self, processed_files):
        pass

scanner = Dummy
