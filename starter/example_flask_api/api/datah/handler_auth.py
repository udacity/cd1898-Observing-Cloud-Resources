from collections import OrderedDict
from .connection import session_commit
from .defs.api_error_codes import *
from .defs.http_codes import *
from marshmallow import ValidationError
from .models import Authorization
from .utils.authz import generate_token
from .utils.logerr import console
from .utils.logerr import generate_failure_dict
from .utils.logerr import generate_success_dict
from .schema import AuthSchema
from sqlalchemy import exc

class AuthHandler():

    '''
        _serialize_data
            event_instance as <declarative_base.Event> as defined in models.py

        returns
            (event_dictionary)
            event_dictionary as <collections.OrderedDict>

        Serializes event data as a dictionary so that it can be reserialized
        as JSON using Flask.jsonfiy() -- and potentially other formats.
    '''
    def _serialize_data(self, auth_instance):
        auth = OrderedDict()
        auth['id'] = auth_instance.id
        auth['created'] = auth_instance.created
        auth['username'] = auth_instance.username
        auth['email'] = auth_instance.email
        auth['role'] = auth_instance.role
        auth['token'] = auth_instance.token
        return auth

    '''
        validate_event
            data as <request.get_json()>

        returns
            (success, schema)
            success as <Boolean> (False is a validation failure)
            schema as <marshmallow.Schema> object
            messages as <marshmallow.ValidationError.messages>

        A method which uses marshmallow to validate posted JSON data against
        the marshmallow.Schema as defined in schema.py.
    '''
    def validate_schema(self, data):
        auth_schema = AuthSchema()
        console(str(data))
        try:
            auth = auth_schema.load(data)
        except ValidationError as error:
            return (False, auth_schema, error.messages)

        return True, auth, None

    '''
        unique_check
            session as <sqlalchemy.sessionmaker session>
            data as <request.get_json()>

        returns
            (success, session, fields, error_message)
            success <boolean> False is a failure
            session <sqlalchemy.sessionmaker session>
            fields <OrderedDict> each field that is not unique
            error_message <datah.utils.api_error_code> + non-unique fields

        Method to check supplied json against the database for duplicates.
        Returns True if the provided data is unique. False if duplicates.
    '''
    def unique_check(self, session, data, error_message=APIMSG_703):
        fields = OrderedDict()
        num_dup_usernames = session.query(Authorization).\
            filter_by(username=data['username']).count()
        num_dup_emails = session.query(Authorization).\
            filter_by(email=data['email']).count()
        num_dup_tokens = session.query(Authorization).\
            filter_by(token=data['token']).count()

        if (num_dup_usernames > 0) or (num_dup_emails > 0) or (num_dup_tokens > 0):
            success = False
        else:
            success = True

        fields = OrderedDict()
        if num_dup_usernames > 0:
            fields[0] = 'username'
            error_message = error_message + " <username>"
        if num_dup_emails > 0:
            fields[1] = 'email'
            error_message = error_message + " <email>"
        if num_dup_tokens > 0:
            fields[2] = 'token'
            error_message = error_message + " <token> # FATAL"

        return success, session, fields, error_message

    '''
        auth_token_check
            session <sqlalchemy.sessionmaker session>
            token <string>

        returns
            (success, session, token, http_code)
            success <Boolean> (False is failure)
            session <sqlalchemy.sessionmaker session>
            token <string>(on success) <generate_failure_dict>(on failure)
            role <integer>
            http_code <http_code> from datah.utils.http_codes

        A method that checks the database for a matching token and returns
        a TRUE or FALSE success message. Also reports duplicate tokens.
        Duplicate tokens will fail the check. Tokens less than 50 chars will
        fail the check.
    '''
    def auth_token_check(self, session, token):
        for record in session.query(Authorization).filter(
            Authorization.token==token
        ):
            auth = record
        num_dup_tokens = session.query(Authorization).\
            filter_by(token=token).count()

        if (not 'auth' in locals()) or (num_dup_tokens != 1):
            if num_dup_tokens >= 2:
                console("<console> *duplicate token* " + token)
            console ("<console> authorization failed " + token)
            return (
                False,
                session,
                generate_failure_dict(0, message=APIMSG_901),
                None,
                HTTP_UNAUTHORIZED
            )

        if (auth.token == token) and (len(token) == 50):
            return (True, session, token, auth.role, HTTP_OK)

    '''
        register_new_auth
            session as <sqlalchemy.sessionmaker session>
            data as <request.get_json()>

        returns
            (success, schema)
            success as <Boolean> (False is a validation failure)
            schema as <marshmallow.Schema> object
            http_code as <http_code> from datah.utils.http_codes

        A method that creates a new authorization user and a new
        authorization token.
    '''
    def register_new_auth(self, session, data):
        if any (key in data for key in ("id", "created", "token", "role")):
            return (
                generate_failure_dict(0, message=APIMSG_701),
                session,
                HTTP_CONFLICT
            )

        data['token'] = generate_token(
            size=50,
            lowercase=False,
            uppercase=True,
            numbers=True
        )

        validated, auth_schema, validation_errors = self.\
            validate_schema(data)
        if not validated:
            return(
                generate_failure_dict(0, message=validation_errors),
                session,
                HTTP_BADREQUEST
            )

        unique, session, _, error_message = self.unique_check(session, data)
        if not unique:
            return (
                generate_failure_dict(0, message=error_message),
                session,
                HTTP_CONFLICT
            )

        new_auth = Authorization(
            username=data['username'],
            email=data['email'],
            token=data['token']
        )

        session.add(new_auth)

        session, commit_errors = session_commit(session)
        if commit_errors:
            return (
                generate_failure_dict(0, message=commit_errors),
                session,
                HTTP_BADREQUEST
            )

        auth = self._serialize_data(new_auth)
        return (
            generate_success_dict(1, auth, APIMSG_101),
            session,
            HTTP_CREATED
        )
