create role spdx with login password 'spdx';
create role spdx_select with login password 'spdx_select';
create database spdx with owner spdx;
grant connect on database spdx to spdx_select;
grant select on all tables in schema public to spdx_select;
