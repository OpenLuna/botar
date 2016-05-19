# -*- coding: UTF-8 -*-
from django.views import generic
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json, requests, random, re
from chatter_bot.models import Location
from bot_content.utils import getPerson
from django.conf import settings
from bot_content.models import FbCard
from chatter_bot.views import parse
# Create your views here.

class Botw(generic.View):
    def get(self, request, *args, **kwargs):
        print "get"
        if self.request.GET['hub.verify_token'] == 'topaja':
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        print "post"
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        print(incoming_message)
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events 
                if 'message' in message.keys():
                    if not  "text" in message['message'].keys():
                        print "not text"
                        if "attachments" in message['message'].keys():
                            print "attachments ma"
                            if message['message']["attachments"][0]["type"] == "location":
                                print "TYPE je location"
                                parseLocation(message['message']["attachments"][0]['payload']["coordinates"],message['sender']['id'])
                                return HttpResponse()
                        post_facebook_message(message['sender']['id'], "Ne razumem tvoje govorice :D")
                        return HttpResponse()
                    print(message)
                    parseMessage(message['message']['text'], message['sender']['id'])
                elif 'postback' in message.keys():
                    parseMessage(message['postback']['payload'], message['sender']['id'])
        return HttpResponse()


def sendMessageToId(request, fb_id, message):
    post_facebook_message(fb_id, message)
    return HttpResponse()


# send message to fb user
def post_facebook_message(fbid, recevied_message):
    print( "post")
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token='+settings.FACEBOOK_SECRET
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":recevied_message}})
    requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)


def parseLocation(location, sender):
    print("parse location")
    person = getPerson(sender)
    print location
    Location(user=person, lon=location["long"], lat=location["lat"]).save()
    post_facebook_message(sender, "Sedaj pa vem kje si ;)")


    # what to do with message? Save/Get Person...
def parseMessage(message, sender):
    print("parse")

    type_of, content = parse(message, sender)
    print "sparsal pa smo", type_of
    if type_of == "card":
        print "zdej pa se send"
        send_facebook_message_card(content, sender)
    elif type_of == "message":
        post_facebook_message(sender, content) 


def send_facebook_message_card(cards, fbid):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token='+settings.FACEBOOK_SECRET
    response_msg = json.dumps({"recipient":{"id":fbid}, 
                                "message":{
                                "attachment":{
                                  "type":"template",
                                  "payload":{
                                    "template_type":"generic",
                                    "elements":[card.getDictionary() for card in cards],
                                  }
                                }
                              }})
    print response_msg
    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
