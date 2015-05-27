from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://spdx:spdx@localhost/spdx20', echo=True)
Base = declarative_base(engine)

class License(Base):
    __tablename__ = 'licenses'
    __table_args__ = {'autoload': True}


class FileType(Base):
    __tablename__ = 'file_types'
    __table_args__ = {'autoload': True}


class Project(Base):
    __tablename__ = 'projects'
    __table_args__ = {'autoload': True}


class File(Base):
    __tablename__ = 'files'
    __table_args__ = {'autoload': True}


class FileLicense(Base):
    __tablename__ = 'files_licenses'
    __table_args__ = {'autoload': True}


class CreatorType(Base):
    __tablename__ = 'creator_types'
    __table_args__ = {'autoload': True}


class Creator(Base):
    __tablename__ = 'creators'
    __table_args__ = {'autoload': True}


class Package(Base):
    __tablename__ = 'packages'
    __table_args__ = {'autoload': True}


class PackageFile(Base):
    __tablename__ = 'packages_files'
    __table_args__ = {'autoload': True}


class Document(Base):
    __tablename__ = 'documents'
    __table_args__ = {'autoload': True}


class ExternalRef(Base):
    __tablename__ = 'external_refs'
    __table_args__ = {'autoload': True}


class DocumentCreator(Base):
    __tablename__ = 'documents_creators'
    __table_args__ = {'autoload': True}


class FileContributor(Base):
    __tablename__ = 'file_contributors'
    __table_args__ = {'autoload': True}


class Identifier(Base):
    __tablename__ = 'identifiers'
    __table_args__ = {'autoload': True}


class RelationshipType(Base):
    __tablename__ = 'relationship_types'
    __table_args__ = {'autoload': True}


class Relationship(Base):
    __tablename__ = 'relationships'
    __table_args__ = {'autoload': True}


class AnnotationType(Base):
    __tablename__ = 'annotation_types'
    __table_args__ = {'autoload': True}


class Annotation(Base):
    __tablename__ = 'annotations'
    __table_args__ = {'autoload': True}


def load_session():
    return sessionmaker(bind=engine)()
