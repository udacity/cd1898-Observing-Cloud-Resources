from collections import OrderedDict
from .connection import session_commit
from .defs.api_error_codes import *
from .defs.http_codes import *
from marshmallow import ValidationError
from .models import Event
from .utils.logerr import console
from .utils.logerr import generate_failure_dict
from .utils.logerr import generate_success_dict
from .schema import EventSchema
from sqlalchemy import exc

class EventsHandler():

    '''
        _serialize_data
            event_instance as <declarative_base.Event> as defined in models.py

        returns
            (event_dictionary)
            event_dictionary as <collections.OrderedDict>

        Serializes event data as a dictionary so that it can be reserialized
        as JSON using Flask.jsonfiy() -- and potentially other formats.
    '''
    def _serialize_data(self, event_instance):
        event = OrderedDict()
        event['id'] = event_instance.id
        event['created'] = event_instance.created
        event['name'] = event_instance.name
        event['location'] = event_instance.location
        event['description'] = event_instance.description
        return event

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
        event_schema = EventSchema()
        console(str(data))
        try:
            event = event_schema.load(data)
        except ValidationError as error:
            return (False, event_schema, error.messages)

        return True, event, None

    '''
        create_event
            session as <sqlalchemy.sessionmaker session>
            data as <request.get_json()>

        returns
            (event, session, http_code)
            event as <OrderedDict> containing result and status
            session as <sqlalchemy.sessionmaker session>
            http_code as <http_code> from datah.utils.http_codes

        Method to create a new event using posted JSON data which is
        deserialized by request.get_json()
    '''
    def create_event(self, session, data):
        if any (key in data for key in ("id", "created")):
            return (
                generate_failure_dict(0, message=APIMSG_701),
                session,
                HTTP_CONFLICT
            )

        validated, event_schema, validation_errors = self.\
            validate_schema(data)
        if not validated:
            return(
                generate_failure_dict(0, message=validation_errors),
                session,
                HTTP_BADREQUEST
            )

        new_event = Event(
            name=data['name'],
            location=data['location'],
            description=data['description']
        )

        session.add(new_event)
        session, commit_errors = session_commit(session)
        if commit_errors:
            return (
                generate_failure_dict(0, message=commit_errors),
                session,
                HTTP_BADREQUEST
            )

        event = self._serialize_data(new_event)
        event = generate_success_dict(1, event, APIMSG_101)
        return event, session, HTTP_CREATED

    '''
        delete_event
            session as <sqlalchemy.sessionmaker session>
            event_id as <integer> representing Event.id

        returns
            (event, session, http_code)
            event as <OrderedDict> containing result and status
            session as <sqlalchemy.sessionmaker session>
            http_code as <http_code> from datah.utils.http_codes

        Method to delete an event by its ID
    '''
    def delete_event(self, session, event_id):
        for result in session.query(Event).filter(Event.id==event_id):
            event = result

        if not 'event' in locals():
            return (
                generate_failure_dict(0, APIMSG_702),
                session,
                HTTP_BADREQUEST
            )

        session.delete(event)
        session, commit_errors = session_commit(session)
        if commit_errors:
            return (
                generate_failure_dict(0, message=commit_errors),
                session,
                HTTP_BADREQUEST
            )

        verify_deletion = session.query(Event).filter_by(id=event_id).count()
        if verify_deletion > 0:
            event = generate_failure_dict(0, APIMSG_800)
        else:
            event = self._serialize_data(event)
            event = generate_success_dict(1, event, APIMSG_103)

        return event, session, HTTP_OK

    '''
        get_all
            session as <sqlalchemy.sessionmaker session>

        returns
            (event, session, http_code)
            event_list as <OrderedDict> containing results and status
            session as <sqlalchemy.sessionmaker session>
            http_code as <http_code> from datah.utils.http_codes

        Returns all events ordered by ascending ID
    '''
    def get_all(self, session):
        i = 0
        event_list = OrderedDict()
        for instance in session.query(Event).order_by(Event.id):
            i += 1
            event = self._serialize_data(instance)
            event_list[i] = event

        event_list = generate_success_dict(
            len(event_list),
            event_list,
            APIMSG_100
        )
        return event_list, session, HTTP_OK

    '''
        get_by_id
            session as <sqlalchemy.sessionmaker session>
            event_id as string/integer

        returns
            (event, session, http_code)
            event as <OrderedDict> containing result and status
            session as <sqlalchemy.sessionmaker session>
            http_code as <http_code> from datah.utils.http_codes

        Method to return a single event by its ID
    '''
    def get_by_id(self, session, event_id):
        for record in session.query(Event).filter(Event.id==event_id):
            event = record

        if not 'event' in locals():
            event = generate_failure_dict(0, APIMSG_702)
        else:
            event = self._serialize_data(event)
            event = generate_success_dict(1, event, APIMSG_100)

        return event, session, HTTP_OK

    '''
        update_by_id
            session as <sqlalchemy.sessionmaker session>
            event_id as string/integer
            data as <request.get_json()>

        returns
            (event, session, http_code)
            updated_event as <OrderedDict> containing result and status
            session as <sqlalchemy.sessionmaker session>
            http_code as <http_code> from datah.utils.http_codes

        Method to PATCH update an event by its ID. Does not require that
        all editable fields are supplied. Single fields can be updated.
    '''
    def update_by_id(self, session, event_id, data):
        for record in session.query(Event).filter(Event.id==event_id):
            event = record

        if not 'event' in locals():
            return (
                generate_failure_dict(0, APIMSG_702),
                session,
                HTTP_BADREQUEST
            )

        # Since this is a patch update, we have to fill in the missing fields.
        # This avoids having to check later when we update the record and it
        # lets us load the data into a marshmallow schema for validation.
        if not 'name' in data.keys():
            data['name'] = event.name
        if not 'location' in data.keys():
            data['location'] = event.location
        if not 'description' in data.keys():
            data['description'] = event.description

        if any (key in data for key in ("id", "created")):
            return (
                generate_failure_dict(0, message=APIMSG_701),
                session,
                HTTP_CONFLICT
            )

        is_validated, event_schema, validation_errors = self.\
            validate_schema(data)
        if not is_validated:
            return(
                generate_failure_dict(0, message=validation_errors),
                session,
                HTTP_BADREQUEST
            )

        # Since we already checked which fields were provided, we can load
        # all of the values into the Event object.
        event.name = data["name"]
        event.location = data["location"]
        event.description = data["description"]

        session.add(event)
        session, commit_errors = session_commit(session)
        if commit_errors:
            return (
                generate_failure_dict(0, message=commit_errors),
                session,
                HTTP_BADREQUEST
            )

        event = self._serialize_data(event)
        event = generate_success_dict(1, event, message=APIMSG_102)
        return event, session, HTTP_OK
