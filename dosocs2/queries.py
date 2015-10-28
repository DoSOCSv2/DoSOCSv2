# Copyright (C) 2015 University of Nebraska at Omaha
#
# This file is part of dosocs2.
#
# dosocs2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# dosocs2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with dosocs2.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-2.0+

from sqlalchemy.sql import select, case, and_, union_all
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
        .join(cty, cre.c.creator_type_id == cty.c.creator_type_id)
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
        .join(cre, ann.c.creator_id == cre.c.creator_id)
        .join(aty, ann.c.annotation_type_id == aty.c.annotation_type_id)
        .join(ide, ann.c.identifier_id == ide.c.identifier_id)
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
        .join(dcr, doc.c.document_id == dcr.c.document_id)
        .join(cre, dcr.c.creator_id == cre.c.creator_id)
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
        .join(pac, doc.c.package_id == pac.c.package_id)
        .join(pfi, pac.c.package_id == pfi.c.package_id)
        .join(fil, pfi.c.file_id == fil.c.file_id)
        .join(fty, fil.c.file_type_id == fty.c.file_type_id)
        .join(ide,
              (pfi.c.package_file_id == ide.c.package_file_id) &
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
        .join(pac, doc.c.package_id == pac.c.package_id)
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
        .join(pac, doc.c.package_id == pac.c.package_id)
        .join(pfi, pac.c.package_id == pfi.c.package_id)
        .join(fil, pfi.c.file_id == fil.c.file_id)
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
        .join(fil, pfi.c.file_id == fil.c.file_id)
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
    rel = db.relationships.alias()
    rty = db.relationship_types.alias()
    ide1 = db.identifiers.alias()
    ide2 = db.identifiers.alias()
    doc1 = db.documents.alias()
    doc2 = db.documents.alias()
    return (select([
        rel.c.relationship_id,
        ide1.c.id_string              .label('left_id_string'),
        rty.c.name                    .label('type'),
        ide2.c.id_string              .label('right_id_string'),
        doc1.c.document_id            .label('left_document_id'),
        doc2.c.document_id            .label('right_document_id'),
        doc1.c.document_namespace_id  .label('left_document_namespace_id'),
        doc2.c.document_namespace_id  .label('right_document_namespace_id'),
        rel.c.relationship_comment    .label('comment')
        ])
    .select_from(
        rel
        .join(rty, rel.c.relationship_type_id == rty.c.relationship_type_id)
        .join(ide1, rel.c.left_identifier_id == ide1.c.identifier_id)
        .join(ide2, rel.c.right_identifier_id == ide2.c.identifier_id)
        .join(doc1, ide1.c.document_namespace_id == doc1.c.document_namespace_id)
        .join(doc2, ide2.c.document_namespace_id == doc2.c.document_namespace_id)
    )
    .where(
        and_(
            doc1.c.document_namespace_id == left_namespace_id,
            ide1.c.id_string == left_id_string
            )
        )
    )


def auto_contains(docid):
    rty = db.relationship_types.alias()
    ide1 = db.identifiers.alias()
    ide2 = db.identifiers.alias()
    doc = db.documents.alias()
    pac = db.packages.alias()
    pfi = db.packages_files.alias()
    return (select([
        doc.c.document_id,
        ide1.c.identifier_id        .label('left_identifier_id'),
        rty.c.relationship_type_id,
        ide2.c.identifier_id        .label('right_identifier_id'),
        ])
    .select_from(
        doc
        .join(pac, doc.c.package_id == pac.c.package_id)
        .join(pfi, pac.c.package_id == pfi.c.package_id)
        .join(ide1,
              (pfi.c.package_id == ide1.c.package_id) &
              (doc.c.document_namespace_id == ide1.c.document_namespace_id)
              )
        .join(ide2,
              (pfi.c.package_file_id == ide2.c.package_file_id) &
              (doc.c.document_namespace_id == ide2.c.document_namespace_id)
              )
        .join(rty, rty.c.name == 'CONTAINS')
        )
    .where(doc.c.document_id == docid)
    )


def auto_contained_by(docid):
    v = auto_contains(docid).alias()
    rty2 = db.relationship_types.alias()
    return (select([
        v.c.document_id,
        v.c.right_identifier_id     .label('left_identifier_id'),
        rty2.c.relationship_type_id,
        v.c.left_identifier_id     .label('right_identifier_id')
        ])
    .select_from(
        v.join(rty2, rty2.c.name == 'CONTAINED_BY')
        )
    .where(v.c.document_id == docid)
    )


def auto_describes(docid):
    rty = db.relationship_types.alias()
    ide1 = db.identifiers.alias()
    ide2 = db.identifiers.alias()
    doc = db.documents.alias()
    pac = db.packages.alias()
    pfi = db.packages_files.alias()
    one = (
        select([
            doc.c.document_id,
            ide1.c.identifier_id        .label('left_identifier_id'),
            rty.c.relationship_type_id,
            ide2.c.identifier_id        .label('right_identifier_id'),
            ])
        .select_from(
            doc
            .join(pac, doc.c.package_id == pac.c.package_id)
            .join(ide1,
                (doc.c.document_id == ide1.c.document_id) &
                (doc.c.document_namespace_id == ide1.c.document_namespace_id)
                )
            .join(ide2,
                (pac.c.package_id == ide2.c.package_id) &
                (doc.c.document_namespace_id == ide2.c.document_namespace_id)
                )
            .join(rty, rty.c.name == 'DESCRIBES')
            )
        .where(doc.c.document_id == docid)
        )
    two = (
        select([
            doc.c.document_id,
            ide1.c.identifier_id        .label('left_identifier_id'),
            rty.c.relationship_type_id,
            ide2.c.identifier_id        .label('right_identifier_id'),
            ])
        .select_from(
            doc
            .join(pac, doc.c.package_id == pac.c.package_id)
            .join(pfi, pac.c.package_id == pfi.c.package_id, isouter=True)
            .join(ide1,
                (doc.c.document_id == ide1.c.document_id) &
                (doc.c.document_namespace_id == ide1.c.document_namespace_id)
                )
            .join(ide2,
                (pfi.c.package_file_id == ide2.c.package_file_id) &
                (doc.c.document_namespace_id == ide2.c.document_namespace_id)
                )
            .join(rty, rty.c.name == 'DESCRIBES')
            )
        .where(doc.c.document_id == docid)
        )
    return union_all(one, two)


def auto_described_by(docid):
    v = auto_describes(docid).alias()
    rty2 = db.relationship_types.alias()
    return (select([
        v.c.document_id,
        v.c.right_identifier_id     .label('left_identifier_id'),
        rty2.c.relationship_type_id,
        v.c.left_identifier_id     .label('right_identifier_id')
        ])
    .select_from(
        v.join(rty2, rty2.c.name == 'DESCRIBED_BY')
        )
    .where(v.c.document_id == docid)
    )
