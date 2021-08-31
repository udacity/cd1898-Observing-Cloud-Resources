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
from datah.utils.logerr import generate_failure_dict
from datah.utils.logerr import generate_success_dict
from datah.schema import AuthSchema
from marshmallow import ValidationError

import sys

api_auth = Blueprint(
    'api_auth',
    __name__,
    template_folder='templates',
    url_prefix='/auth'
)


'''
    Main /auth API Handler
    / base is /auth/
'''
@api_auth.route('/', methods=['GET'])
def api_auth_root():
    return "OK", HTTP_OK


@api_auth.route('/register', methods=['POST'])
def api_auth_register():
    db, db_session = dbc_establish()
    try:
        data = request.get_json()
    except Exception as error:
        print(str(error.description))
        return (
            jsonify(generate_failure_dict(0, message=APIMSG_700)),
            HTTP_BADREQUEST
        )

    auth_handler = AuthHandler()
    new_auth, db_session, http_code = auth_handler.\
        register_new_auth(db_session, data)

    return jsonify(new_auth), http_code
