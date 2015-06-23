import time

import jinja2
from . import util
from . import viewmap


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
    v = viewmap.viewmap(db)
    document = util.row_to_dict(
        v['v_documents']
        .filter(v['v_documents'].document_id == docid)
        .one()
        )
    external_refs = util.rows_to_dicts(
        v['v_external_refs']
        .filter(v['v_external_refs'].document_id == docid)
        .all()
        )
    document['creators'] = util.rows_to_dicts(
        v['v_documents_creators']
        .filter(v['v_documents_creators'].document_id == docid)
        .all()
        )
    document['annotations'] = util.rows_to_dicts(
        v['v_annotations']
        .filter(v['v_annotations'].document_id == docid)
        .filter(v['v_annotations'].id_string == document['id_string'])
        .all()
        )
    document['relationships'] = util.rows_to_dicts(
        v['v_relationships']
        .filter(v['v_relationships'].left_document_namespace_id == document['document_namespace_id'])
        .filter(v['v_relationships'].left_id_string == document['id_string'])
        .all()
        ) or None
    package = util.row_to_dict(
        v['v_documents_packages']
        .filter(v['v_documents_packages'].document_id == docid)
        .one()
        )
    package['license_info_from_files'] = util.rows_to_dicts(
        v['v_packages_all_licenses_in_files']
        .filter(v['v_packages_all_licenses_in_files'].package_id == package['package_id'])
        .all()
        ) or ['NOASSERTION']
    package['annotations'] = util.rows_to_dicts(
        v['v_annotations']
        .filter(v['v_annotations'].document_id == docid)
        .filter(v['v_annotations'].id_string == package['id_string'])
        .all()
        )
    package['relationships'] = util.rows_to_dicts(
        v['v_relationships']
        .filter(v['v_relationships'].left_document_namespace_id == document['document_namespace_id'])
        .filter(v['v_relationships'].left_id_string == package['id_string'])
        .all()
        ) or None
    package['files'] = util.rows_to_dicts(
        v['v_documents_files']
        .filter(v['v_documents_files'].document_id == docid)
        .filter(v['v_documents_files'].package_id == package['package_id'])
        .all()
        )
    for file in package['files']:
        file['license_info'] = util.rows_to_dicts(
            v['v_files_licenses']
            .filter(v['v_files_licenses'].file_id == file['file_id'])
            .all()
            )
        file['contributors'] = util.rows_to_dicts(
            v['v_file_contributors']
            .filter(v['v_file_contributors'].file_id == file['file_id'])
            .all()
            )
        file['annotations'] = util.rows_to_dicts(
            v['v_annotations']
            .filter(v['v_annotations'].document_id == docid)
            .filter(v['v_annotations'].id_string == file['id_string'])
            .all()
            )
        file['relationships'] = util.rows_to_dicts(
            v['v_relationships']
            .filter(v['v_relationships'].left_document_namespace_id == document['document_namespace_id'])
            .filter(v['v_relationships'].left_id_string == file['id_string'])
            .all()
            )
    licenses = util.rows_to_dicts(
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
