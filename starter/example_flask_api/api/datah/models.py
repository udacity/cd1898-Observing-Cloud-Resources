import datetime
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from .schema import EventSchema
from .utils.authz import generate_token

Base = declarative_base()

class Event(Base):
    __tablename__ = 'events'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    name = Column(String(50), nullable=False)
    location = Column(String(50), nullable=True)
    description = Column(String(200), nullable=False)

    def __repr__(self):
        return ("<Events(name='%s', location='%s', description='%s', "
                "created='%s')>" % (
                self.name, self.location, self.description, str(self.created)))

class Authorization(Base):
    __tablename__ = 'auths'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    username = Column(String(25), unique=True, nullable=False)
    email = Column(String(75), unique=True, nullable=False)
    role = Column(Integer, default=0, nullable=False)
    token = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return ("<Auths(username='%s', email='%s', created='%s',"
                " token='%s')>" % (
                self.username, self.email, str(self.role), self.token, str(self.created)))
