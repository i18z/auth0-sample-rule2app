"""Python Flask WebApp Auth0 integration example
"""
from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException

from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode

import constants

import requests
import re
from whitelist import whitelist

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = env.get(constants.AUTH0_CALLBACK_URL)
AUTH0_CLIENT_ID = env.get(constants.AUTH0_CLIENT_ID)
AUTH0_CLIENT_SECRET = env.get(constants.AUTH0_CLIENT_SECRET)
AUTH0_DOMAIN = env.get(constants.AUTH0_DOMAIN)
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = env.get(constants.AUTH0_AUDIENCE)
if AUTH0_AUDIENCE is '':
    AUTH0_AUDIENCE = AUTH0_BASE_URL + '/userinfo'


app = Flask(__name__, static_url_path='/public', static_folder='./public')
app.secret_key = constants.SECRET_KEY
app.debug = True


@app.errorhandler(Exception)
def handle_auth_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response


oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile email abc',
    },
)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if constants.PROFILE_KEY not in session:
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated

####>BEGIN<### Added for rule2app

def requires_auth_by_whitelist(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if constants.PROFILE_KEY not in session:
            return redirect('/login')
        user_email = session[constants.PROFILE_KEY]['email']

        # Authorize user access to lists rules by whitelist. whitelist is defined in whitelist.py
        if user_email not in whitelist:
            return render_template('dashboard.html',
                           userinfo=session[constants.PROFILE_KEY],
                           info_pretty='You are not authorized to use this function.')
        return f(*args, **kwargs)

    return decorated

def getAuth0MgtApiToken():
'''
Input: N/A. Get client_id, client_secret from .env file.
Output: String. The Access Token to call Auth0 Management API.
'''
    header = {'content-type': 'application/json'}
    data = {'grant_type':"client_credentials",
        'client_id': env.get('M2M_CLIENT_ID'),
        'client_secret': env.get('M2M_CLIENT_SECRET'),
        'audience': AUTH0_BASE_URL + '/api/v2/'}

    req_token = requests.post(AUTH0_BASE_URL + '/oauth/token', headers=header, json=data)
    token = req_token.json()
    return token["access_token"]

def getAllRules(token):
'''
Input: String. The Access Token to call Auth0 Management API.
Output: JSON Object. All the rules (https://auth0.com/docs/api/management/v2/#!/Rules/get_rules).
'''
    header = {'Authorization': 'Bearer ' + token}
    req_rules = requests.get('https://quickstart.au.auth0.com/api/v2/rules', headers=header)
    rules = req_rules.json()
    return rules

def mapRuleToApp(jscode):
'''
Input: String. Snippet of javascript code of a Auth0 rule.
Output: String. The Auth0 application that the input js code applies to.
Assumptions:
    1) A rule is always applied to one application, with the following code:
        if (context.clientName === 'TheAppToCheckAccessTo') {...
    2) The 'TheAppToCheckAccessTo' part of the first match is returned as the application name
    3) The application name is allowed to have letters, numbers, understore and space
    4) If no match are found, "unknown" is returned
'''
    pattern = r'if\s?\(context\.clientName\s?===\s?([a-zA-Z0-9_ \'\"]+)\)\s?{'
    g = re.search(pattern, jscode, re.MULTILINE)
    if g:
        return g.group(1)[1:-1]
    else:
        return 'unknown'
####>END<### Added for rule2app


# Controllers API
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/callback')
def callback_handling():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    session[constants.JWT_PAYLOAD] = userinfo
    session[constants.PROFILE_KEY] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'email': userinfo['email']
    }
    return redirect('/dashboard')


@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)


@app.route('/logout')
def logout():
    session.clear()
    params = {'returnTo': url_for('home', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


@app.route('/dashboard')
@requires_auth
def dashboard():
    return render_template('dashboard.html',
                           userinfo=session[constants.PROFILE_KEY],
                           info_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4))

####>BEGIN<### Added for rule2app
@app.route('/rules')
@requires_auth_by_whitelist
def rules():
    rule2app_titles = ['rule', 'enabled', 'application']
    rule2app = []
    api_token = getAuth0MgtApiToken()
    rules = getAllRules(api_token)
    for rule in rules:
        rule2app.append({'rule': rule['name'], 'enabled': rule['enabled'], 'application': mapRuleToApp(rule['script'])})
    return render_template('rules.html',
                        titles=rule2app_titles,
                        rules=rule2app)
####>END<### Added for rule2app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=env.get('PORT', 3000))
