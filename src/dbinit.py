import orm
session = orm.load_session()
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
