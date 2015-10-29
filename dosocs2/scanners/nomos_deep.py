import os

from . import nomos
from .. import scannerbase
from .. import util

class NomosDeep(nomos.Nomos):

    """Same as Nomos, but unpacks archives in the file list.

    Regular Nomos treats every file as a monolith, even archives. NomosDeep
    will unpack those files that are archives, and scan the resulting directory
    structure.  All licenses found in such an archive are tied to the archive
    itself, rather than any of the files inside.

    Nomos and NomosDeep will return the same number of files scanned, but for
    archive files, NomosDeep may return better results, but run slower.
    """

    name = 'nomos_deep'

    def process_file(self, file):
        scan_result = set()
        if util.archive_type(file.path):
            with util.tempextract(file.path) as (tempdir, relpaths):
                abspaths = (os.path.join(tempdir, relpath) for relpath in relpaths)
                filepaths = (abspath for abspath in abspaths if os.path.isfile(abspath))
                for filepath in filepaths:
                    work_item = scannerbase.WorkItem(None, filepath)
                    this_result = super(NomosDeep, self).process_file(work_item)
                    scan_result.update(this_result)
        else:
            scan_result = super(NomosDeep, self).process_file(file)
        return scan_result

scanner = NomosDeep
