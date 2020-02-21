import requests
import sys
from flask import Flask, redirect, url_for, session,  jsonify, request
import os
from flask_oauthlib.client import OAuth
import json

NEW_CLIENT_ID = '997118811859-1bfvrb7r0g4i81ul14321av96aci14rl.apps.googleusercontent.com'
NEW_CLIENT_SECRET = 'NGW_O7uAzLO_enUS0MTLQLYI'
API_KEY = 'AIzaSyAW36FiSidOVb_AIq-YqJyT6EFc5oHoJLA'

DEBUG = True
app = Flask(__name__)
app.debug = DEBUG
app.secret_key = 'super secret key'

oauth = OAuth()

google = oauth.remote_app( 'google',
    consumer_key=NEW_CLIENT_ID,
    consumer_secret=NEW_CLIENT_SECRET,
    request_token_params={ 'scope': 'https://www.googleapis.com/auth/contacts.readonly'},
    base_url='https://accounts.google.com/o/oauth2/auth',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_method='POST',
    access_token_url='https://oauth2.googleapis.com/token',
    request_token_url=None,
)

@app.route('/')
def index():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    access_token = access_token[0]

    headers = {'Authorization': 'OAuth '+access_token}
    data = requests.get('https://people.googleapis.com/v1/people/me/connections?pageSize=2000&personFields=names%2CemailAddresses%2CphoneNumbers&sortOrder=FIRST_NAME_ASCENDING&key='+API_KEY, headers=headers)
    data = data.json()

    try:
        # FILTER ONLY CONTACTS WITH EMAIL
        data = [x for x in data['connections'] if 'emailAddresses' in x]

        # FILTER ONLY @GMAIL
        data_gmail = [x for x in data if x['emailAddresses'][0]['value'].find('@gmail.com') != -1]

        # FILTER ONLY @HOTMAIL
        data_hotmail = [x for x in data if x['emailAddresses'][0]['value'].find('@hotmail.com') != -1]

        data = {'hotmail': data_hotmail,
                'hotmail_size': len(data_hotmail),
                'gmail': data_gmail,
                'gmail_size': len(data_gmail),
                'total': len(data_gmail) + len(data_hotmail)}
    except:
        data = {
            'code': 404,
            'message': 'Contacts not found'
        }


    return jsonify(data)

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: error=%s' % (request.args['error'])
    if isinstance(resp, dict) and 'access_token' in resp:
        session['access_token'] = (resp['access_token'], '')
    return redirect(url_for('index'))

@google.tokengetter
def get_access_token():
    return session.get('access_token')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('https://mail.google.com/mail/u/0/?logout')

def main():
    app.run(host='0.0.0.0')

if __name__ == '__main__':
    main()
