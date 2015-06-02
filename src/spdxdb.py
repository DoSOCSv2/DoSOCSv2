# <SPDX-License-Identifier: Apache-2.0>
# Copyright (c) 2014-2015 University of Nebraska at Omaha (UNO) and other
# contributors.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import itertools
import os
from settings import settings
import scanners
import util


class Transaction:
    def __init__(self, db):
        self.db = db

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type is None:
            self.db.commit()
        else:
            self.db.rollback()

    def lookup_or_add_license(self, short_name):
        '''Add license to the database if it does not exist.

        Return the new or existing license object in any case.
        '''
        existing_license = (self.db.licenses
            .filter(self.db.licenses.short_name == short_name)
            .first()
            )
        if existing_license is not None:
            return existing_license
        license_params = {
            # correct long name is never known for found licenses
            'name': None,
            'short_name': short_name,
            'cross_reference': '',
            'comment': '',
            'is_spdx_official': False,
            }
        new_license = self.db.licenses.insert(**license_params)
        self.db.flush()
        return new_license

    def _create_file(self, path, sha1):
        file_type_id = (self.db.file_types
            .filter(self.db.file_types.name == util.spdx_filetype(path))
            .one().file_type_id
            )
        file_params = {
            'sha1': sha1,
            'file_type_id': file_type_id,
            'copyright_text': None,
            'project_id': None,
            'comment': '',
            'notice': ''
            }
        new_file = self.db.files.insert(**file_params)
        self.db.flush()
        return new_file

    def scan_file(self, path, scanner=scanners.nomos):
        '''Scan file for licenses, and add it to the DB if it does not exist.

        Return the file object.

        If the file is cached, return the cached file object, and do not
        scan.
        '''
        sha1 = util.sha1(path)
        file = util.lookup_by_sha1(self.db.files, sha1)
        if file is not None:
            return file
        file = self._create_file(path, sha1)
        if scanner is not None:
            shortnames_found = [item.license for item in scanner.scan(path)]
            licenses_found = [
                self.lookup_or_add_license(shortname)
                for shortname in shortnames_found
                ]
            if len(shortnames_found) > 0:
                license_name_list = ','.join(shortnames_found)
                scanner_comment = scanner.name + ': ' + license_name_list
            else:
                scanner_comment = scanner.name + ': ' + 'No licenses found'
            file.comment = scanner_comment
            for license in licenses_found:
                file_license_params = {
                    'file_id': file.file_id,
                    'license_id': license.license_id,
                    'extracted_text': '',
                    }
                self.db.files_licenses.insert(**file_license_params)
        self.db.flush()
        return file

    def scan_package(self, path, scanner=scanners.nomos):
        '''Scan package for licenses. Add it and all files to the DB.

        Return the package object.

        Only scan if the package is not already cached (by SHA-1).
        '''
        sha1 = util.sha1(path)
        package = util.lookup_by_sha1(self.db.packages, sha1)
        if package is not None:
            return package
        package_params = {
            'name': util.package_friendly_name(os.path.basename(path)),
            'version': '',
            'file_name': os.path.basename(path),
            'supplier_id': None,
            'originator_id': None,
            'download_location': None,
            'verification_code': '',  # filled in after file processing
            'ver_code_excluded_file_id': None,
            'sha1': sha1,
            'home_page': None,
            'source_info': '',
            'concluded_license_id': None,
            'declared_license_id': None,
            'license_comment': '',
            'copyright_text': None,
            'summary': '',
            'description': '',
            'comment': ''
            }
        package = self.db.packages.insert(**package_params)
        self.db.flush()
        with util.tempextract(path) as (tempdir, relpaths):
            abspaths = [os.path.join(tempdir, path) for path in relpaths]
            hashes = []
            for relpath, abspath in itertools.izip(relpaths, abspaths):
                if not os.path.isfile(abspath):
                    continue
                fileobj = self.scan_file(abspath, scanner)
                hashes.append(fileobj.sha1)
                package_file_params = {
                    'package_id': package.package_id,
                    'file_id': fileobj.file_id,
                    'concluded_license_id': None,
                    'file_name': os.path.join(os.curdir, relpath),
                    'license_comment': ''
                    }
                self.db.packages_files.insert(**package_file_params)
        package.verification_code = util.gen_ver_code(hashes)
        self.db.flush()
        return package

    def create_document_namespace(self, doc_name):
        suffix = util.friendly_namespace_suffix(doc_name)
        uri = settings['default_namespace_prefix'] + suffix
        document_namespace = self.db.document_namespaces.insert(uri=uri)
        self.db.flush()
        return document_namespace

    def create_all_identifiers(self, document_namespace_id, package_id):
        all_files = (self.db.packages_files
            .filter(self.db.packages_files.package_id == package_id)
            .all()
            )
        package_id_params = {
            'document_namespace_id': document_namespace_id,
            'package_id': package_id,
            'id_string': util.gen_id_string()
            }
        for file in all_files:
            file_id_params = {
                'document_namespace_id': document_namespace_id,
                'file_id': file.file_id,
                'id_string': util.gen_id_string()
                }
            self.db.identifiers.insert(**file_id_params)
        self.db.identifiers.insert(**package_id_params)
        self.db.flush()

    def create_document(self, package_id, **kwargs):
        package = self.db.packages.get(package_id)
        data_license = (self.db.licenses
            .filter(self.db.licenses.short_name == 'CC0-1.0')
            .one()
            )
        doc_name = kwargs.get('name') or util.package_friendly_name(package.file_name)
        doc_namespace = self.create_document_namespace(doc_name)
        document_params = {
            'data_license_id': data_license.license_id,
            'spdx_version': 'SPDX-2.0',
            'name': doc_name,
            'document_namespace_id': doc_namespace.document_namespace_id,
            'license_list_version': '2.0',  # TODO: dynamically fill from database table
            'creator_comment': kwargs.get('creator_comment') or '',
            'document_comment': kwargs.get('document_comment') or '',
            'package_id': package_id
        }
        new_document = self.db.documents.insert(**document_params)
        self.db.flush()
        # default_creator_id should always be 1, because the default is
        # always the first creator row created.
        # TODO: don't hardcode this.
        default_creator_id = 1
        document_creator_params = {
            'document_id': new_document.document_id,
            'creator_id': default_creator_id
            }
        self.db.documents_creators.insert(**document_creator_params)
        document_identifier_params = {
            'document_namespace_id': doc_namespace.document_namespace_id,
            'document_id': new_document.document_id,
            'id_string': 'SPDXRef-DOCUMENT'
        }
        self.db.identifiers.insert(**document_identifier_params)
        self.create_all_identifiers(doc_namespace.document_namespace_id, package_id)
        self.db.flush()
        return new_document

    def fetch_doc(self, docid):
        return self.db.documents.get(docid)
