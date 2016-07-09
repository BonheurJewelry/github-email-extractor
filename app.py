import json
import logging 
import sys
import os
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

from flask import Flask, abort, request
from flask.ext.cors import CORS

import github_email

EMAIL_FILE = "email_file"
app = Flask(__name__)
CORS(app)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

@app.route("/", methods=['POST', 'GET'])
def main():
    if request.method == 'GET':
        abort(404)
    else:
        github_username = request.form.get('username').lower()
        if not os.path.exists(EMAIL_FILE):
            with open(EMAIL_FILE, 'w+') as f:
                json.dump({}, f)
        else:
            with open(EMAIL_FILE, 'r+') as f:
                email_dict = json.load(f)

        # check if the email was found earlier or not
        if email_dict.get(github_username):
            return email_dict[github_username]
        response = github_email.get(github_username)
        if response['success']:
            email = response['email'][0]

            # add email to be used in future
            email_dict[github_username] = email
            with open(EMAIL_FILE, 'w+') as f:
                json.dump(email_dict, f)
            
            return "{0}".format(email)
        else:
            abort(404)

@app.route("/get-all", methods=["GET"])
def get_all():
    email_dict = {}
    if not os.path.exists(EMAIL_FILE):
        with open(EMAIL_FILE, 'w+') as f:
            json.dump(email_dict, f)

    with open(EMAIL_FILE, 'r+') as f:
        email_dict = json.load(f)
    return json.dumps(email_dict)

@app.errorhandler(404)
def page_not_found(error):
    return "Check https://github.com/prabhakar267/github-email-extractor for more details"


if __name__ == "__main__" :
    app.run(debug=True, host="0.0.0.0", threaded=True)
