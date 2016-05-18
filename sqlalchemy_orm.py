from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Text, Integer, ForeignKey
from sqlalchemy.orm import backref, relationship


Base = declarative_base()


class Path(Base):
    __tablename__ = 'paths'
    path_id = Column(Integer, primary_key=True, index=True)
    parent_path_id = Column(Integer, ForeignKey('paths.path_id'), nullable=True)
    path = Column(Text, nullable=False, index=True, unique=True)
    data = Column(Text, nullable=False)

    children = relationship(
        'Path',
        backref=backref(
            'parent',
            remote_side=[path_id],
            cascade='all, delete-orphan',
            single_parent=True
        ),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
