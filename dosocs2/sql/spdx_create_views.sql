create view
v_license_approved_names
as
select
lic.license_id          license_id,
case
  when lic.is_spdx_official = TRUE then lic.short_name
  else 'LicenseRef-' || lic.short_name
end                 as  short_name
from licenses lic
;


create view
v_creators
as
select
cre.creator_id          creator_id,

case when cty.name = 'Tool' then
    cty.name || ': ' || cre.name
else
    cty.name || ': ' || cre.name || ' (' || cre.email || ')'
end                     as creator_text

from creators cre
join creator_types cty on cre.creator_type_id = cty.creator_type_id
;


create view
v_annotations
as
select
ann.annotation_id           annotation_id,
ann.document_id             document_id,
cre.creator_text            creator,
ann.created_ts at time zone 'utc'          as created_ts,
ann.comment                 "comment",
aty.name                    "type",
ide.id_string               id_string
from annotations ann
join v_creators cre on ann.creator_id = cre.creator_id
join annotation_types aty on ann.annotation_type_id = aty.annotation_type_id
join identifiers ide on ann.identifier_id = ide.identifier_id
;


create view
v_documents_creators
as
select
doc.document_id             document_id,
cre.creator_id              creator_id,
cre.creator_text            creator
from documents doc
join documents_creators dcr on doc.document_id = dcr.document_id
join v_creators cre on dcr.creator_id = cre.creator_id
;


create view
v_documents_files
as
select
doc.document_id                 document_id,
pfi.package_id                  package_id,
pfi.package_file_id             package_file_id,
fil.file_id                     file_id,
pfi.file_name                   "name",
ide.id_string                   id_string,
fty.name                        "type",
fil.sha1                        checksum,
lic.short_name                  license_concluded,
pfi.license_comment             license_comments,
fil.copyright_text              copyright_text,
pro.name                        project_name,
pro.homepage                    project_homepage,
pro.uri                         project_uri,
fil.comment                     "comment",
fil.notice                      notice
from documents doc
join packages pac on doc.package_id = pac.package_id
join packages_files pfi on pac.package_id = pfi.package_id
join files fil on pfi.file_id = fil.file_id
join file_types fty on fil.file_type_id = fty.file_type_id
join identifiers ide on pfi.package_file_id = ide.package_file_id
    and doc.document_namespace_id = ide.document_namespace_id
left join v_license_approved_names lic on pfi.concluded_license_id = lic.license_id
left join projects pro on fil.project_id = pro.project_id
;


create view
v_documents_packages
as
select
doc.document_id                 document_id,
pac.package_id                  package_id,
pac.name                        "name",
ide.id_string                   id_string,
pac.version                     "version",
pac.file_name                   file_name,
cre1.creator_text               supplier,
cre2.creator_text               originator,
pac.download_location           download_location,
pac.verification_code           verification_code,
pac.sha1                        checksum,
pac.home_page                   home_page,
pac.source_info                 source_info,
lic1.short_name                 license_concluded,
lic2.short_name                 license_declared,
pac.license_comment             license_comments,
pac.copyright_text              copyright_text,
pac.summary                     summary,
pac.description                 description,
pac.comment                     "comment"
from documents doc
join packages pac on doc.package_id = pac.package_id
join identifiers ide on pac.package_id = ide.package_id
    and doc.document_namespace_id = ide.document_namespace_id
left join v_license_approved_names lic1 on pac.concluded_license_id = lic1.license_id
left join v_license_approved_names lic2 on pac.declared_license_id = lic2.license_id
left join v_creators cre1 on pac.supplier_id = cre1.creator_id
left join v_creators cre2 on pac.originator_id = cre2.creator_id
;


create view
v_documents
as
select
doc.document_id             document_id,
doc.document_namespace_id   document_namespace_id,
doc.spdx_version            spdx_version,
lic.short_name              data_license,
ide.id_string               id_string,
doc.name                    "name",
dns.uri                     uri,
doc.license_list_version    license_list_version,
doc.created_ts at time zone 'utc'
                            as created_ts,
doc.creator_comment         creator_comment,
doc.document_comment        document_comment
from documents doc
join v_license_approved_names lic on doc.data_license_id = lic.license_id
join document_namespaces dns on doc.document_namespace_id = dns.document_namespace_id
join identifiers ide on doc.document_id = ide.document_id
     and doc.document_namespace_id = ide.document_namespace_id
;


create view
v_documents_unofficial_licenses
as
select
doc.document_id             document_id,
lic.license_id              license_id,
coalesce(lic.name, lic.short_name) as "name",
-- there has got to be a better way to select which extracted_text
-- field to use here...
'LicenseRef-' || lic.short_name as id_string,
min(fli.extracted_text)   extracted_text,
lic.cross_reference         cross_reference,
lic.comment                 "comment"
from documents doc
join packages pac on doc.package_id = pac.package_id
join packages_files pfi on pac.package_id = pfi.package_id
join files fil on pfi.file_id = fil.file_id
join files_licenses fli on fil.file_id = fli.file_id
join licenses lic on fli.license_id = lic.license_id
where lic.is_spdx_official is FALSE
group by doc.document_id, lic.license_id, lic.short_name,
lic.cross_reference, lic.comment
;


create view
v_external_refs
as
select
ext.external_ref_id         external_ref_id,
ext.document_id             document_id,
ext.id_string               id_string,
ext.sha1                    sha1,
dna.uri                     uri
from external_refs ext
join document_namespaces dna on ext.document_namespace_id = dna.document_namespace_id
;


create view
v_file_contributors
as
select
file_contributor_id,
file_id,
contributor
from file_contributors
;


create view
v_files_licenses
as
select
fil.file_id                 file_id,
lic.short_name              short_name
from files fil
left join files_licenses fli on fil.file_id = fli.file_id
left join v_license_approved_names lic on fli.license_id = lic.license_id
;


create view
v_packages_all_licenses_in_files
as
select
pac.package_id              package_id,
pac.name                    package_name,
coalesce(lic1.short_name, lic2.short_name)   license_short_name,
count(*)                    license_found_count
from packages pac
join packages_files pfi on pac.package_id = pfi.package_id
join files fil on pfi.file_id = fil.file_id
left join v_license_approved_names lic1 on pfi.concluded_license_id = lic1.license_id
left join files_licenses fli on fil.file_id = fli.file_id
join v_license_approved_names lic2 on fli.license_id = lic2.license_id
group by pac.package_id, pac.name, coalesce(lic1.short_name, lic2.short_name)
;


create view
v_relationships
as
select
rel.relationship_id             relationship_id,
ide1.id_string                  left_id_string,
rty.name                        "type",
ide2.id_string                  right_id_string,
doc1.document_id                left_document_id,
doc2.document_id                right_document_id,
doc1.document_namespace_id      left_document_namespace_id,
doc2.document_namespace_id      right_document_namespace_id,
rel.relationship_comment        "comment"
from relationships rel
join relationship_types rty on rel.relationship_type_id = rty.relationship_type_id
join identifiers ide1 on rel.left_identifier_id = ide1.identifier_id
join identifiers ide2 on rel.right_identifier_id = ide2.identifier_id
join documents doc1 on ide1.document_namespace_id = doc1.document_namespace_id
join documents doc2 on ide2.document_namespace_id = doc2.document_namespace_id
;


create view
v_auto_contains
as
select
doc.document_id                 document_id,
ide1.identifier_id              left_identifier_id,
rty.relationship_type_id        relationship_type_id,
ide2.identifier_id              right_identifier_id
from documents doc
join packages pac on doc.package_id = pac.package_id
join packages_files pfi on pac.package_id = pfi.package_id
join identifiers ide1 on pfi.package_id = ide1.package_id
     and doc.document_namespace_id = ide1.document_namespace_id
join identifiers ide2 on pfi.package_file_id = ide2.package_file_id
     and doc.document_namespace_id = ide2.document_namespace_id
join relationship_types rty on rty.name = 'CONTAINS'
;


create view
v_auto_contained_by
as
select
v.document_id               document_id,
v.right_identifier_id       left_identifier_id,
rty2.relationship_type_id   relationship_type_id,
v.left_identifier_id        right_identifier_id
from v_auto_contains v
join relationship_types rty2 on rty2.name = 'CONTAINED_BY'
;


create view
v_auto_describes
as
select
doc.document_id             document_id,
ide1.identifier_id          left_identifier_id,
rty.relationship_type_id    relationship_type_id,
ide2.identifier_id          right_identifier_id
from documents doc
join packages pac on doc.package_id = pac.package_id
join identifiers ide1 on doc.document_id = ide1.document_id
join identifiers ide2 on pac.package_id = ide2.package_id
     and ide2.document_namespace_id = doc.document_namespace_id
join relationship_types rty on rty.name = 'DESCRIBES'

union all

select
doc.document_id             document_id,
ide1.identifier_id          left_identifier_id,
rty.relationship_type_id    relationship_type_id,
ide2.identifier_id          right_identifier_id
from documents doc
join packages pac on doc.package_id = pac.package_id
left join packages_files pfi on pfi.package_id = pac.package_id
join identifiers ide1 on doc.document_id = ide1.document_id
join identifiers ide2 on pfi.package_file_id = ide2.package_file_id
     and ide2.document_namespace_id = doc.document_namespace_id
join relationship_types rty on rty.name = 'DESCRIBES'
;


create view
v_auto_described_by
as
select
v.document_id               document_id,
v.right_identifier_id       left_identifier_id,
rty2.relationship_type_id   relationship_type_id,
v.left_identifier_id        right_identifier_id
from v_auto_describes v
join relationship_types rty2 on rty2.name = 'DESCRIBED_BY'
;
