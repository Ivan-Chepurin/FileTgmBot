from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine('sqlite:///tgmBot.db', echo=True)

Base = declarative_base()

Session = sessionmaker()
Session.configure(bind=engine)


class Account(Base):
    __tablename__ = 'accounts'
    password = Column(String, primary_key=True, unique=True, nullable=False)
    users = relationship('User')
    files = relationship('File')

    def __repr__(self):
        return '<Account(password="{}")>'.format(self.password)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, unique=True)
    account_id = Column(String, ForeignKey('accounts.password'))
    error_counter = Column(Integer, nullable=False)
    current_state = Column(Integer)

    def __repr__(self):
        return '<User(id="{}")>'.format(self.id)


class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True, unique=True)
    account_id = Column(String, ForeignKey('accounts.password'), nullable=False)

    file_id = Column(String, unique=True, nullable=False)
    file_unique_id = Column(String, unique=True, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)

    def __repr__(self):
        return 'File(name="{}")'.format(self.name)



Base.metadata.create_all(engine)
