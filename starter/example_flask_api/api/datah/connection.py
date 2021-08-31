import datetime
from .models import Base
from .models import Event
from .models import Authorization
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc
from .utils.logerr import console
import yaml


class DatabaseConnection():

    def __init__(self):

        try:
            creds_file = os.environ['API_CNFYAML']
        except KeyError as error:
            creds_file = '../dbcreds.yaml'
            console("<cred_file> is ommitted. Using default -- not that secure.")

        dbcreds = yaml.safe_load(open(creds_file))
        self.Engine = create_engine(
            'mysql+pymysql://'+dbcreds['db_user']+':'+dbcreds['db_pass']+'@'+
            dbcreds['db_host']+'/'+dbcreds['db_name'], echo=False)
        self.Engine.connect()

    def create_database(self):
        Base.metadata.create_all(self.Engine)

    def start_session(self):
        self.Session = sessionmaker(bind=self.Engine)
        return self.Session()


def dbc_establish():
    db = DatabaseConnection()
    db_session = db.start_session()
    return db, db_session

def session_commit(session):
    try:
        session.commit()
    except exc.IntegrityError as error:
        return session, error.args
    except exc.DataError as error:
        return session, error.args

    return session, None
