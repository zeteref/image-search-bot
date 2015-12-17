import base64
import cStringIO
import json
import logging
import os
import random
import re
import simplejson
import StringIO
import sys
import telegram
import time
import urllib
import urllib2
import webapp2

from google.appengine.api import urlfetch
from google.appengine.ext import ndb

from pyquery import PyQuery as pq

f = open('secret.json')
s = json.loads(f.read())
f.close()

TOKEN = s['TOKEN']

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))

class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        print fetch_image('kitty')


    def fetch_image(searchTerm, safe=True):
        searchTerm = urllib.quote_plus(searchTerm)

        url = ('http://www.bing.com/images/search?q=%s' % searchTerm)

        opener = urllib2.build_opener()
        if not safe:
            opener.addheaders.append(('Cookie', 'SRCHHPGUSR=CW=1587&CH=371&DPR=1&ADLT=OFF'))

        page = opener.open(url)
        xhtml = page.read()
        page = pq(xhtml).xhtml_to_html()

        return random.choice([x.attrib['href'] for x in page('.thumb')])

app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)

