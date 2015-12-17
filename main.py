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
import multipart

from google.appengine.api import urlfetch
from google.appengine.ext import ndb

from PIL import Image
from pyquery import PyQuery as pq

f = open('secret.json')
s = json.loads(f.read())
f.close()

TOKEN = s['TOKEN']

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'

bot = telegram.Bot(token=TOKEN)

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
        try:
            urlfetch.set_default_fetch_deadline(60)
            body = json.loads(self.request.body)
            logging.info('request body:')
            logging.info(body)
            self.response.write(json.dumps(body))

            update_id = body['update_id']
            message = body['message']
            self.message_id = message.get('message_id')
            date = message.get('date')
            text = message.get('text')
            fr = message.get('from')
            chat = message['chat']
            self.chat_id = chat['id']

            command, params = parse_command(text)

            if not command: return
            if not hasattr(self, command): return

            func = getattr(self, command)
            func(params)
        except:
            logging.exception('Exception was thrown')

    def img_command(self, params):
        self.msg(self.fetch_image_url(params, safe=False))

    def safeimg_command(self, params):
        self.msg(self.fetch_image_url(params, safe=False))

    def fetch_image_url(self, searchTerm, safe=True):
        searchTerm = urllib.quote_plus(searchTerm)

        url = ('http://www.bing.com/images/search?q=%s' % searchTerm)

        opener = urllib2.build_opener()
        if not safe:
            opener.addheaders.append(('Cookie', 'SRCHHPGUSR=CW=1587&CH=371&DPR=1&ADLT=OFF'))

        page = opener.open(url)
        xhtml = page.read()
        page = pq(xhtml).xhtml_to_html()

        return random.choice([x.attrib['href'] for x in page('.thumb')])

    def msg(self, msg=None, img=None, preview='true', reply=False):
        if self.message_id == "-1": # for testing
            self.response.write("\n")
            self.response.write('-----------------------------\n')
            self.response.write(msg)
            self.response.write('\n-----------------------------')
        elif msg:
            params = {
                'chat_id': str(self.chat_id),
                'text': msg.encode('utf-8'),
                'enable_web_page_preview': preview,
            }
            if reply:
                params['reply_to_message_id'] = str(self.message_id)

            bot.sendChatAction(chat_id=self.chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
            self.sendImage(msg)

    def sendImage(self, url):
        img = cStringIO.StringIO(urllib.urlopen(url).read()).getvalue()
        resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
            ('chat_id', str(self.chat_id)),
            ('reply_to_message_id', str(self.message_id)),
        ], [
            ('photo', 'image.jpg', img),
        ])


def parse_command(text):
    if not text.startswith('/'): return

    tmp = text[1:].split()
    return tmp[0] + "_command", ' '.join(tmp[1:])

app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)

