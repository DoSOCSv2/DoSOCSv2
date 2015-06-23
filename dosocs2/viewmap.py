'''Database view mappings for SQLSoup.'''
from sqlalchemy import Table
from .settings import settings

'''All views produced by viewmap().'''
view_names = {
    'v_license_approved_names',
    'v_creators',
    'v_annotations',
    'v_documents_creators',
    'v_documents_files',
    'v_documents_packages',
    'v_documents',
    'v_documents_unofficial_licenses',
    'v_external_refs',
    'v_file_contributors',
    'v_files_licenses',
    'v_packages_all_licenses_in_files',
    'v_relationships',
    'v_auto_contains',
    'v_auto_contained_by',
    'v_auto_describes',
    'v_auto_described_by',
    'v_dupes'
    }

def viewmap(db):
    '''Return a dictionary of views that can be queried like SQLSoup tables.'''
    views = {}
    for view_name in view_names:
        table = Table(view_name, db._metadata, autoload=True)
        # Here we are monkey-patching a primary key onto the view so
        # that SQLSoup will be able to map it.
        # The primary key for each view is every column together.
        # Not sure if this is bad or not.
        # It's just views and not tables though, so who cares?
        views[view_name] = db.map(table, primary_key=tuple(col for col in table.c.values()))
    return views
