import jinja2
import util
import viewmap


def _filter_text(value):
    return '<text>' + value + '</text>'


def _filter_text_default(value, default_value='NOASSERTION'):
    if value:
        return '<text>' + value + '</text>'
    else:
        return default_value


def _filter_noassertion(value):
    return value if value else 'NOASSERTION'


jinja2_env = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
jinja2_env.filters['text'] = _filter_text
jinja2_env.filters['text_default'] = _filter_text_default
jinja2_env.filters['noassertion'] = _filter_noassertion


def render_template(templatefile, context):
    with open(templatefile, 'r') as f:
        s = f.read()
    t = jinja2_env.from_string(s)
    return t.render(context)


def render_document(db, docid, template_file):
    v = viewmap.viewmap(db)
    document_obj = (
        v['v_documents']
        .filter(v['v_documents'].document_id == docid)
        .one()
        )
    document = util.row_to_dict(document_obj)
    external_refs_list = (
        v['v_external_refs']
        .filter(v['v_external_refs'].document_id == docid)
        .all()
        )
    external_refs = [
        util.row_to_dict(row)
        for row in external_refs_list
        ]
    documents_creators_list = (
        v['v_documents_creators']
        .filter(v['v_documents_creators'].document_id == docid)
        .all()
        )
    document['creators'] = [
        util.row_to_dict(row)
        for row in documents_creators_list
        ]
    annotations_list = (
        v['v_annotations']
        .filter(v['v_annotations'].document_id == docid)
        .all()
        )
    document['annotations'] = [
        util.row_to_dict(row)
        for row in annotations_list
    ]
    relationships_list = (
        v['v_relationships']
        .filter(v['v_relationships'].left_document_namespace_id == document['document_namespace_id'])
        .filter(v['v_relationships'].left_id_string == 'SPDXRef-DOCUMENT')
        .all()
        )
    document['relationships'] = [
        util.row_to_dict(row)
        for row in relationships_list
        ]
    package_obj = (
        v['v_documents_packages']
        .filter(v['v_documents_packages'].document_id == docid)
        .one()
        )
    package = util.row_to_dict(package_obj)
    license_info_list = (
        v['v_packages_all_licenses_in_files']
        .filter(v['v_packages_all_licenses_in_files'].package_id == package['package_id'])
        .all()
        )
    license_info_from_files = [
        util.row_to_dict(row)
        for row in license_info_list
        ]
    package['license_info_from_files'] = license_info_from_files or ['NOASSERTION']
    context = {
        'document': document,
        'external_refs': external_refs,
        'package': package,
        'licenses': [] # stub
        }
    return render_template(template_file, context)
