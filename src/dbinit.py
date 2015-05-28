import orm

session = orm.Session()
filetypes = (
    'SOURCE',
    'BINARY',
    'ARCHIVE',
    'APPLICATION',
    'AUDIO',
    'IMAGE',
    'TEXT',
    'VIDEO',
    'DOCUMENTATION'
)
for f in filetypes:
    session.add(orm.FileType(name=f))
session.commit()
