from flask import Flask, request, redirect
from models import db, Url
import requests
import validators
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
TOKEN = '555534854:AAEIMAaWRMeB5YLM4reFegxA-L-f8Zm1_MI'
URL = 'https://api.telegram.org/bot{}/'.format(TOKEN)

BASE = 62
MOD = BASE**5

char = [0]*BASE
for d in range(26):
    char[d] = chr(d + ord('a'))
for d in range(26):
    char[d+26] = chr(d + ord('A'))
for d in range(10):
    char[d+52] = chr(d + ord('0'))
char += ['-', '.', '_', '~', ':', '/', '?', '#', '[', ']', '@', '!', '$', '&', '\'', '(', ')', '*', '+', ',', ':', '=', '%']

code = dict()
for i in range(len(char)):
    code[char[i]] = i

def hash_url(long_url):
    hsh = 0
    for c in long_url:
        hsh = (hsh*256 + ord(c)) % MOD
    return hsh

def string(hsh):
    s = ''
    while hsh != 0:
        s += char[hsh % BASE]
        hsh //= BASE
    return s

def send_message(text, chat_id):
    url = URL + 'sendMessage?text={}&chat_id={}'.format(text, chat_id)
    requests.get(url)

@app.route('/shorten', methods=['POST'])
def shorten():
    req = request.get_json()
    try:
        long_url = req['message']['text']
        chat_id = req['message']['chat']['id']
        if not validators.url(long_url):
            send_message('The entered URL in not valid!', chat_id)
            return 'url not valid';
        hsh = hash_url(long_url)
        hsh_string = string(hsh)
        short_url = '%s.herokuapp.com' % os.environ['APP_NAME']
        send_message('Your URL is shortened as:\n%s' % short_url, chat_id)
        db.session.add(Url(hsh=hsh, long_url=long_url))
        db.session.commit()
    except KeyError:
        pass
    return 'Ok'

@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>')
def expand(path):
    url = Url.query.filter_by(hsh=path).first()
    return redirect(url.long_url)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
