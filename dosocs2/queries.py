from sqlalchemy.sql import select, case, label, and_
from sqlalchemy import func
from . import schema as db

def license_approved_names():
    lic = db.licenses.alias()
    return (select([
        lic.c.license_id,
        case(
            [[lic.c.is_spdx_official == True, lic.c.short_name]],
            else_='LicenseRef-' + lic.c.short_name
            ).label('short_name')
        ])
    )


def creators():
    cre = db.creators.alias()
    cty = db.creator_types.alias()
    return (select([
        cre.c.creator_id,
        case(
            [[cty.c.name == 'Tool',
              cty.c.name + ': ' + cre.c.name
              ]],
            else_=cty.c.name + ': ' + cre.c.name + ' (' + cre.c.email + ')'
            ).label('creator_text')
        ])
    .select_from(
        cre
        .join(cty)
        )
    )


def annotations(docid, id_string):
    ann = db.annotations.alias()
    aty = db.annotation_types.alias()
    cre = creators().alias()
    ide = db.identifiers.alias()
    return (select([
        ann.c.annotation_id,
        ann.c.document_id,
        cre.c.creator_text.label('creator'),
        #func.timezone('UTC', ann.c.created_ts).label('created_ts'),
        ann.c.created_ts,
        ann.c.comment,
        aty.c.name.label('type'),
        ide.c.id_string
        ])
    .select_from(
        ann
        .join(cre)
        .join(aty)
        .join(ide,
              ann.c.identifier_id == ide.c.identifier_id
              )
        )
    .where(
        and_(
            ann.c.document_id == docid,
            ide.c.id_string == id_string
            )
        )
    )


def documents_creators(docid):
    cre = creators().alias()
    doc = db.documents.alias()
    dcr = db.documents_creators.alias()
    return (select([
        doc.c.document_id,
        cre.c.creator_id,
        cre.c.creator_text.label('creator')
        ])
    .select_from(
        doc 
        .join(dcr)
        .join(cre)
        )
    .where(doc.c.document_id == docid)
    )


def documents_files(docid, package_id):
    doc = db.documents.alias()
    pac = db.packages.alias()
    pfi = db.packages_files.alias()
    fil = db.files.alias()
    fty = db.file_types.alias()
    ide = db.identifiers.alias()
    lic = license_approved_names().alias() 
    pro = db.projects.alias()
    return (select ([
        doc.c.document_id,
        pac.c.package_id,
        pfi.c.package_file_id,
        fil.c.file_id,
        pfi.c.file_name         .label('name'),
        ide.c.id_string,
        fty.c.name              .label('type'),
        fil.c.sha1              .label('checksum'),
        lic.c.short_name        .label('license_concluded'),
        pfi.c.license_comment   .label('license_comments'),
        fil.c.copyright_text,
        pro.c.name              .label('project_name'),
        pro.c.homepage          .label('project_homepage'),
        pro.c.uri               .label('project_uri'),
        fil.c.comment,
        fil.c.notice
        ])
    .select_from(
        doc
        .join(pac)
        .join(pfi, pac.c.package_id == pfi.c.package_id)
        .join(fil)
        .join(fty)
        .join(ide,
              (pac.c.package_id == ide.c.package_id) &
              (doc.c.document_namespace_id == ide.c.document_namespace_id)
              )
        .join(lic, pfi.c.concluded_license_id == lic.c.license_id, isouter=True)
        .join(pro, fil.c.project_id == pro.c.project_id, isouter=True)
        )
    .where(
        and_(
            doc.c.document_id == docid,
            pac.c.package_id == package_id
            )
        )
    )


def documents_packages(docid):
    doc = db.documents.alias()
    pac = db.packages.alias()
    pfi = db.packages_files.alias()
    ide = db.identifiers.alias()
    lic1 = license_approved_names().alias() 
    lic2 = license_approved_names().alias() 
    cre1 = creators().alias()
    cre2 = creators().alias()
    return (select ([
        doc.c.document_id,
        pac.c.package_id,
        pac.c.name,
        ide.c.id_string,
        pac.c.version,
        pac.c.file_name,
        cre1.c.creator_text         .label('supplier'),
        cre2.c.creator_text         .label('originator'),
        pac.c.download_location,
        pac.c.verification_code,
        pac.c.sha1                  .label('checksum'),
        pac.c.home_page,
        pac.c.source_info,
        lic1.c.short_name             .label('license_concluded'),
        lic2.c.short_name             .label('license_declared'),
        pac.c.license_comment         .label('license_comments'),
        pac.c.copyright_text,
        pac.c.summary,
        pac.c.description,
        pac.c.comment
        ])
    .select_from(
        doc
        .join(pac)
        .join(ide,
              (pac.c.package_id == ide.c.package_id) &
              (doc.c.document_namespace_id == ide.c.document_namespace_id)
              )
        .join(lic1, pac.c.concluded_license_id == lic1.c.license_id, isouter=True)
        .join(lic2, pac.c.declared_license_id == lic2.c.license_id, isouter=True)
        .join(cre1, pac.c.supplier_id == cre1.c.creator_id, isouter=True)
        .join(cre2, pac.c.originator_id == cre2.c.creator_id, isouter=True)
        )
    .where(doc.c.document_id == docid)
    )


def documents(docid):
    doc = db.documents.alias()
    lic = license_approved_names().alias() 
    dns = db.document_namespaces.alias()
    ide = db.identifiers.alias()
    return (select ([
        doc.c.document_id,
        doc.c.document_namespace_id,
        doc.c.spdx_version,
        lic.c.short_name                .label('data_license'),
        ide.c.id_string,
        doc.c.name,
        dns.c.uri,
        doc.c.license_list_version,
       # func.timezone('UTC', doc.c.created_ts).label('created_ts'),
        doc.c.created_ts,
        doc.c.creator_comment,
        doc.c.document_comment
        ])
    .select_from(
        doc
        .join(lic, doc.c.data_license_id == lic.c.license_id)
        .join(dns, doc.c.document_namespace_id == dns.c.document_namespace_id)
        .join(ide,
              (doc.c.document_id == ide.c.document_id) &
              (doc.c.document_namespace_id == ide.c.document_namespace_id)
              )
        )
    .where(doc.c.document_id == docid)
    )


def documents_unofficial_licenses(docid):
    doc = db.documents.alias()
    pac = db.packages.alias()
    pfi = db.packages_files.alias()
    fil = db.files.alias()
    fli = db.files_licenses.alias() 
    lic = db.licenses.alias() 
    return (select ([
        doc.c.document_id,
        lic.c.license_id,
        func.coalesce(lic.c.name, lic.c.short_name).label('name'),
        ('LicenseRef-' + lic.c.short_name).label('id_string'),
        func.min(fli.c.extracted_text).label('extracted_text'),
        lic.c.cross_reference,
        lic.c.comment
        ])
    .select_from(
        doc
        .join(pac)
        .join(pfi, pac.c.package_id == pfi.c.package_id)
        .join(fil)
        .join(fli, fil.c.file_id == fli.c.file_id)
        .join(lic, fli.c.license_id == lic.c.license_id)
        )
    .where(
        and_(
            lic.c.is_spdx_official == False,
            doc.c.document_id == docid
            )
        )
    .group_by(
        doc.c.document_id,
        lic.c.license_id,
        lic.c.short_name,
        lic.c.cross_reference,
        lic.c.comment
        )
    )


def external_refs(docid):
    ext = db.external_refs.alias()
    dna = db.document_namespaces.alias()
    return (select([
        ext.c.external_ref_id,
        ext.c.document_id,
        ext.c.id_string,
        ext.c.sha1,
        dna.c.uri
        ])
    .select_from(
        ext
        .join(dna, ext.c.document_namespace_id == dna.c.document_namespace_id)
        )
    .where(ext.c.document_id == docid)
    )


def file_contributors(file_id):
    fco = db.file_contributors.alias()
    return (select([
        fco.c.file_contributor_id,
        fco.c.file_id,
        fco.c.contributor
        ])
    .where(fco.c.file_id == file_id)
    )


def files_licenses(file_id):
    fil = db.files.alias()
    fli = db.files_licenses.alias() 
    lic = license_approved_names().alias() 
    return (select([
        fil.c.file_id,
        lic.c.short_name
        ])
    .select_from(
        fil
        .join(fli, fil.c.file_id == fli.c.file_id, isouter=True)
        .join(lic, fli.c.license_id == lic.c.license_id, isouter=True)
        )
    .where(fil.c.file_id == file_id)
    )


def packages_all_licenses_in_files(package_id):
    pac = db.packages.alias()
    pfi = db.packages_files.alias()
    fil = db.files.alias()
    fli = db.files_licenses.alias()
    lic1 = license_approved_names().alias() 
    lic2 = license_approved_names().alias() 
    return (select([
        pac.c.package_id,
        pac.c.name              .label('package_name'),
        func.coalesce(lic1.c.short_name, lic2.c.short_name).label('license_short_name'),
        func.count()            .label('license_found_count')
        ])
    .select_from(
        pac
        .join(pfi, pac.c.package_id == pfi.c.package_id)
        .join(fil)
        .join(lic1, pfi.c.concluded_license_id == lic1.c.license_id, isouter=True)
        .join(fli, fil.c.file_id == fli.c.file_id, isouter=True)
        .join(lic2, fli.c.license_id == lic2.c.license_id)
        )
    .where(pac.c.package_id == package_id)
    .group_by(
        pac.c.package_id,
        pac.c.name,
        func.coalesce(lic1.c.short_name, lic2.c.short_name)
        )
    )


def relationships(left_namespace_id, left_id_string):
    # stub
    return select([db.relationships]).where(False)


def auto_contains():
    # stub
    return select([db.relationships]).where(False)


def auto_contained_by():
    # stub
    return select([db.relationships]).where(False)


def auto_describes():
    # stub
    return select([db.relationships]).where(False)


def auto_described_by():
    # stub
    return select([db.relationships]).where(False)
