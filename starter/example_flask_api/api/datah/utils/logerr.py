from collections import OrderedDict
import logging
import time
import sys

def generate_failure_dict(records, message="General Error."):
    error_message = OrderedDict()
    error_message['success'] = False
    error_message['records'] = records
    error_message['message'] = message

    final_message = OrderedDict()
    final_message['status'] = error_message
    return final_message

def generate_success_dict(records, dataset, message="No Message."):
    messages = OrderedDict()
    messages['success'] = True
    messages['message'] = message
    messages['records'] = records

    final_message = OrderedDict()
    final_message['status'] = messages
    final_message['dataset'] = dataset
    return final_message

def console(string):
    timestamp = time.strftime("%Y %b-%d %I:%M:%S %Z")
    string = "<console> <" + timestamp + "> " + string
    print(string, file=sys.stderr)
