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
        .all()
        )
    document['relationships'] = util.rows_to_dicts(
        v['v_relationships']
        .filter(v['v_relationships'].left_document_namespace_id == document['document_namespace_id'])
        .filter(v['v_relationships'].left_id_string == 'SPDXRef-DOCUMENT')
        .all()
        )
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
    context = {
        'document': document,
        'external_refs': external_refs,
        'package': package,
        'licenses': [] # stub
        }
    return render_template(template_file, context)
