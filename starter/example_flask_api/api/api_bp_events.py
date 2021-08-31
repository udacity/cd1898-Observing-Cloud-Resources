# encoding: UTF-8
from flask import Blueprint
from flask import jsonify
from flask import request
from flask import Response
from datah.connection import dbc_establish
from datah.connection import DatabaseConnection
from datah.defs.api_error_codes import *
from datah.defs.http_codes import *
from datah.handler_auth import AuthHandler
from datah.handler_events import EventsHandler
from datah.utils.logerr import generate_failure_dict
from datah.utils.logerr import generate_success_dict
from datah.utils.logerr import console
from datah.schema import EventSchema
from marshmallow import ValidationError

import sys

api_events = Blueprint(
    'api_events',
    __name__,
    template_folder='templates',
    url_prefix='/events'
)

'''
    Main /events API Handler
    / base is /events/
'''
@api_events.route('/', methods=['GET', 'POST'])
def api_events_root():
    db, db_session = dbc_establish()
    events_handler = EventsHandler()
    if request.method == 'GET':
        events_list, db_session, http_code = events_handler.get_all(db_session)
        return jsonify(events_list), http_code

    elif request.method == 'POST':
        try:
            data = request.get_json()
        except Exception as error:
            console(str(error.description))
            return(
                jsonify(generate_failure_dict(0, message=APIMSG_700)),
                HTTP_BADREQUEST
            )

        events_handler = EventsHandler()
        new_event, db_session, http_code = events_handler.\
            create_event(db_session, data)

        return jsonify(new_event), http_code


@api_events.route('/<int:event_id>', methods=['DELETE', 'GET', 'PATCH'])
def api_events_byid(event_id):
    db, db_session = dbc_establish()
    events_handler = EventsHandler()
    if request.method == 'GET':
        event, db_session, http_code = events_handler.\
            get_by_id(db_session, event_id)
        return jsonify(event), http_code

    elif request.method == 'PATCH':
        try:
            data = request.get_json()
        except Exception as error:
            return (
                jsonify(generate_failure_dict(0,message=APIMSG_700)),
                HTTP_BADREQUEST
            )

        event, db_session, code = events_handler.\
            update_by_id(db_session, event_id, data)

        return jsonify(event), code

    elif request.method == 'DELETE':
        event, db_session, code = events_handler.\
            delete_event(db_session, event_id)
        return jsonify(event), code
