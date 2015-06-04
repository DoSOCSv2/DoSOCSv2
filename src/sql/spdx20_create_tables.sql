create table if not exists
licenses (
    license_id              serial,
    name                    varchar(255),
    short_name              varchar(255) not null,
    cross_reference         text not null,
    comment                 text not null,
    is_spdx_official        boolean not null,
    primary key (license_id),
    constraint uc_license_short_name unique (short_name)
);


-- SPDX file types (e.g. 'ARCHIVE', 'BINARY', 'SOURCE')
create table if not exists
file_types (
    file_type_id            serial,
    name                    varchar(255) not null,
    primary key (file_type_id),
    constraint uc_file_type_name unique (name)
);


create table if not exists
projects (
    project_id              serial,
    name                    text not null,
    homepage                text not null,
    uri                     text not null,
    primary key (project_id)
);


-- file, package-independent
create table if not exists
files (
    file_id                 serial,
    file_type_id            integer not null,
    sha1                    char(40) not null,
    copyright_text          text,
    project_id              integer,
    comment                 text not null,
    notice                  text not null,
    primary key (file_id),
    foreign key (project_id) references projects (project_id),
    foreign key (file_type_id) references file_types (file_type_id)
);


-- license/file many-to-many
create table if not exists
files_licenses (
    file_id                 serial,
    license_id              integer not null,
    extracted_text          text not null,
    primary key (file_id, license_id),
    foreign key (file_id) references files (file_id),
    foreign key (license_id) references licenses (license_id)
);


-- type of creator ('Person', 'Tool', 'Organization')
create table if not exists
creator_types (
    creator_type_id         serial,
    name                    varchar(255) not null,
    primary key (creator_type_id)
);


-- document creators
create table if not exists
creators (
    creator_id              serial,
    creator_type_id         integer not null,
    name                    varchar(255) not null,
    email                   varchar(255) not null,
    primary key (creator_id),
    foreign key (creator_type_id) references creator_types (creator_type_id)
);


create table if not exists
packages (
    package_id              serial,
    name                    varchar(255) not null,
    version                 varchar(255) not null,
    file_name               text not null,
    supplier_id             integer,
    originator_id           integer,
    download_location       text,
    verification_code       char(40) not null,
    ver_code_excluded_file_id  integer,
    sha1                    char(40),
    home_page               text,
    source_info             text not null,
    concluded_license_id    integer,
    declared_license_id     integer,
    license_comment         text not null,
    copyright_text          text,
    summary                 text not null,
    description             text not null,
    comment                 text not null,
    primary key (package_id),
    foreign key (supplier_id) references creators (creator_id),
    foreign key (originator_id) references creators (creator_id),
    foreign key (concluded_license_id) references licenses (license_id),
    foreign key (declared_license_id) references licenses (license_id)
);


-- file/package many-to-many
create table if not exists
packages_files (
    package_file_id         serial,
    package_id              integer not null,
    file_id                 integer not null,
    concluded_license_id    integer,
    license_comment         text not null,
    file_name               text not null,
    primary key (package_file_id),
    constraint uc_package_id_file_id_file_name unique (package_id, file_id, file_name),
    foreign key (package_id) references packages (package_id),
    foreign key (file_id) references files (file_id),
    foreign key (concluded_license_id) references licenses (license_id)
);


alter table packages
add constraint fk_package_packages_files foreign key (ver_code_excluded_file_id)
references packages_files (package_file_id);


create table if not exists
document_namespaces (
    document_namespace_id   serial,
    uri                     varchar(500) not null,
    primary key (document_namespace_id),
    constraint uc_document_namespace_uri unique (uri)
);


-- SPDX documents
create table if not exists
documents (
    document_id             serial,
    document_namespace_id   integer not null,
    data_license_id         integer not null,
    spdx_version            varchar(255) not null,
    name                    varchar(255) not null,
    license_list_version    varchar(255) not null,
    created_ts              timestamp not null default current_timestamp,
    creator_comment         text not null,
    document_comment        text not null,
    package_id              integer not null,
    primary key (document_id),
    constraint uc_document_document_namespace_id unique (document_namespace_id),
    foreign key (document_namespace_id) references document_namespaces (document_namespace_id),
    foreign key (data_license_id) references licenses (license_id),
    foreign key (package_id) references packages (package_id)
);


-- references to external documents
create table if not exists
external_refs (
    external_ref_id         serial,
    document_id             integer not null,
    document_namespace_id   integer not null,
    id_string               varchar(255) not null,
    sha1                    char(40) not null,
    primary key (external_ref_id),
    constraint uc_external_ref_document_id_string unique (document_id, id_string),
    foreign key (document_id) references documents (document_id),
    foreign key (document_namespace_id) references document_namespaces (document_namespace_id)
);


-- document/creator many-to-many
create table if not exists
documents_creators (
    document_id             integer not null,
    creator_id              integer not null,
    primary key (document_id, creator_id),
    foreign key (document_id) references documents (document_id),
    foreign key (creator_id) references creators (creator_id)
);


create table if not exists
file_contributors (
    file_contributor_id     serial,
    file_id                 integer not null,
    contributor             text not null,
    primary key (file_contributor_id),
    foreign key (file_id) references files (file_id)
);


-- SPDX identifiers
create table if not exists
identifiers (
    identifier_id           serial,
    document_namespace_id   integer not null,
    id_string               varchar(255) not null,
    document_id             integer,
    package_id              integer,
    package_file_id         integer,
    primary key (identifier_id),
    constraint uc_identifier_document_namespace_id_name unique (document_namespace_id, id_string),
    constraint ck_identifier_exactly_one check (
        (cast(document_id is not null as int) +
         cast(package_id is not null as int) +
         cast(package_file_id is not null as int)
        ) = 1
    ),
    constraint uc_identifier_namespace_document_id unique (document_namespace_id, document_id),
    constraint uc_identifier_namespace_package_id unique (document_namespace_id, package_id),
    constraint uc_identifier_namespace_package_file_id unique (document_namespace_id, package_file_id),
    foreign key (document_namespace_id) references document_namespaces (document_namespace_id),
    foreign key (document_id) references documents (document_id),
    foreign key (package_id) references packages (package_id),
    foreign key (package_file_id) references packages_files (package_file_id)
);


-- SPDX relationship types (e.g. CONTAINS, CONTAINED BY)
create table if not exists
relationship_types (
    relationship_type_id    serial,
    name                    varchar(255) not null,
    primary key (relationship_type_id),
    constraint uc_relationship_type_name unique (name)
);


-- Relationships between SPDX elements
create table if not exists
relationships (
    relationship_id         serial,
    left_identifier_id      integer not null,
    right_identifier_id     integer not null,
    relationship_type_id    integer not null,
    relationship_comment    text not null,
    primary key (relationship_id),
    foreign key (left_identifier_id) references identifiers (identifier_id),
    foreign key (right_identifier_id) references identifiers (identifier_id),
    foreign key (relationship_type_id) references relationship_types (relationship_type_id),
    constraint uc_left_right_relationship_type unique (
        left_identifier_id,
        right_identifier_id,
        relationship_type_id
    )
);


-- Annotation type (REVIEW or OTHER)
create table if not exists
annotation_types (
    annotation_type_id      serial,
    name                    varchar(255) not null,
    primary key (annotation_type_id),
    constraint uc_annotation_type_name unique (name)
);


create table if not exists
annotations (
    annotation_id           serial,
    document_id             integer not null,
    annotation_type_id      integer not null,
    identifier_id           integer not null,
    creator_id              integer not null,
    created_ts              timestamp not null,
    comment                 text not null,
    primary key (annotation_id),
    foreign key (document_id) references documents (document_id),
    foreign key (annotation_type_id) references annotation_types (annotation_type_id),
    foreign key (identifier_id) references identifiers (identifier_id),
    foreign key (creator_id) references creators (creator_id)
);
