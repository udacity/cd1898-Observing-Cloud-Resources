from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask import Response
from api_bp_events import api_events
from api_bp_auth import api_auth
from datah.connection import dbc_establish
from datah.connection import DatabaseConnection
from datah.defs.api_error_codes import *
from datah.defs.http_codes import *
from datah.handler_auth import AuthHandler
from datah.handler_events import EventsHandler
from datah.utils.authz import token_deserialize
from datah.utils.logerr import console
from datah.utils.logerr import generate_failure_dict
from datah.utils.logerr import generate_success_dict
from datah.schema import EventSchema
import logging
from marshmallow import ValidationError

import sys

api = Flask(__name__)
api.config.from_pyfile('flask-config.py')

'''
    Blueprints are being used to handle the primary endpoints
'''
api.register_blueprint(api_auth)
api.register_blueprint(api_events)


'''
    Bearer Token Check
'''
@api.before_request
def before_request():
    #THIS BYPASSES AUTHORIZATION FOR THE /auth/register ENDPOINT
    #skip_auth = False
    if "/init" in request.path:
        skip_auth=True

    if "/auth/register" in request.base_url:
        skip_auth=True

    if not 'skip_auth' in locals():
        token, errors = token_deserialize(request.headers)
        if errors:
            return (
                jsonify(generate_failure_dict(0, message=APIMSG_900)),
                HTTP_UNAUTHORIZED
            )

        db, db_session = dbc_establish()

        auth_handler = AuthHandler()
        success, session, _, _, _ = auth_handler.\
            auth_token_check(db_session, token)

        if not success:
            return (
                jsonify(generate_failure_dict(0, message=APIMSG_900)),
                HTTP_UNAUTHORIZED
            )


'''
    Main API
'''
@api.route('/')
def api_root():
    return render_template('root_index.html')

@api.route('/init', methods=['POST'])
def api_init():
    db, db_session = dbc_establish()
    db.create_database()
    try:
        data = request.get_json()
    except:
        return (
            jsonify(generate_failure_dict(0, message=APIMSG_700)),
            HTTP_BADREQUEST
        )

    events_handler = EventsHandler()
    new_event, db_session, http_code = events_handler.create_event(db_session, data)

    return jsonify(new_event), http_code


'''
    Error Handlers
'''
@api.errorhandler(HTTP_NOTFOUND)
def errorhandler_404(error):
    return jsonify(generate_failure_dict(0, message=APIMSG_600)), HTTP_NOTFOUND

@api.errorhandler(HTTP_METHODNOTALLOWED)
def errorhandler_405(error):
    return jsonify(generate_failure_dict(0, message=APIMSG_601)), HTTP_METHODNOTALLOWED

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    api.logger.handlers = gunicorn_logger.handlers
    api.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    api.run()
