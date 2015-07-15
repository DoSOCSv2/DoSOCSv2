# <SPDX-License-Identifier: Apache-2.0>
# Copyright (c) 2015 University of Nebraska Omaha and other contributors.

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

import time

import jinja2
from . import config
from . import viewmap
from . import util


def row_to_dict(row):
    '''Convert SQLSoup row to a dictionary.'''
    d = {}
    for column in row._table.columns:
        d[column.name] = getattr(row, column.name)
    return d


def rows_to_dicts(rows):
    return [row_to_dict(row) for row in rows]


def _filter_text(value):
    return '<text>' + value + '</text>'


def _filter_text_default(value, default_value='NOASSERTION'):
    if value:
        return '<text>' + value + '</text>'
    else:
        return default_value


def _filter_noassertion(value):
    return value if value else 'NOASSERTION'


def _filter_utctimestamp(value):
    return time.strftime('%FT%TZ', value.timetuple())


jinja2_env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
jinja2_env.filters['text'] = _filter_text
jinja2_env.filters['text_default'] = _filter_text_default
jinja2_env.filters['noassertion'] = _filter_noassertion
jinja2_env.filters['utctimestamp'] = _filter_utctimestamp


def render_template(templatefile, context):
    with open(templatefile, 'r') as f:
        s = f.read()
    t = jinja2_env.from_string(s)
    return t.render(context)


def render_document(db, docid, template_file):
    render_relationships = util.bool_from_str(config.config['dosocs2']['render_relationships'])
    v = viewmap.viewmap(db)
    document = row_to_dict(
        v['v_documents']
        .filter(v['v_documents'].document_id == docid)
        .one()
        )
    external_refs = rows_to_dicts(
        v['v_external_refs']
        .filter(v['v_external_refs'].document_id == docid)
        .all()
        )
    document['creators'] = rows_to_dicts(
        v['v_documents_creators']
        .filter(v['v_documents_creators'].document_id == docid)
        .all()
        )
    document['annotations'] = rows_to_dicts(
        v['v_annotations']
        .filter(v['v_annotations'].document_id == docid)
        .filter(v['v_annotations'].id_string == document['id_string'])
        .all()
        )
    document['relationships'] = render_relationships and rows_to_dicts(
        v['v_relationships']
        .filter(v['v_relationships'].left_document_namespace_id == document['document_namespace_id'])
        .filter(v['v_relationships'].left_id_string == document['id_string'])
        .all()
        ) or None
    package = row_to_dict(
        v['v_documents_packages']
        .filter(v['v_documents_packages'].document_id == docid)
        .one()
        )
    package['license_info_from_files'] = rows_to_dicts(
        v['v_packages_all_licenses_in_files']
        .filter(v['v_packages_all_licenses_in_files'].package_id == package['package_id'])
        .all()
        ) or ['NOASSERTION']
    package['annotations'] = rows_to_dicts(
        v['v_annotations']
        .filter(v['v_annotations'].document_id == docid)
        .filter(v['v_annotations'].id_string == package['id_string'])
        .all()
        )
    package['relationships'] = render_relationships and rows_to_dicts(
        v['v_relationships']
        .filter(v['v_relationships'].left_document_namespace_id == document['document_namespace_id'])
        .filter(v['v_relationships'].left_id_string == package['id_string'])
        .all()
        ) or None
    package['files'] = rows_to_dicts(
        v['v_documents_files']
        .filter(v['v_documents_files'].document_id == docid)
        .filter(v['v_documents_files'].package_id == package['package_id'])
        .all()
        )
    for file in package['files']:
        file['license_info'] = rows_to_dicts(
            v['v_files_licenses']
            .filter(v['v_files_licenses'].file_id == file['file_id'])
            .all()
            )
        file['contributors'] = rows_to_dicts(
            v['v_file_contributors']
            .filter(v['v_file_contributors'].file_id == file['file_id'])
            .all()
            )
        file['annotations'] = rows_to_dicts(
            v['v_annotations']
            .filter(v['v_annotations'].document_id == docid)
            .filter(v['v_annotations'].id_string == file['id_string'])
            .all()
            )
        file['relationships'] = render_relationships and rows_to_dicts(
            v['v_relationships']
            .filter(v['v_relationships'].left_document_namespace_id == document['document_namespace_id'])
            .filter(v['v_relationships'].left_id_string == file['id_string'])
            .all()
            ) or None
    licenses = rows_to_dicts(
        v['v_documents_unofficial_licenses']
        .filter(v['v_documents_unofficial_licenses'].document_id == document['document_id'])
        .all()
        )
    context = {
        'document': document,
        'external_refs': external_refs,
        'package': package,
        'licenses': licenses
        }
    return render_template(template_file, context)
