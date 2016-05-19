# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.http.response import HttpResponse
from .models import Person, Feed, Events, FbCard


# Create your views here.


def sendMessageToFeed(request, feed_name, message):
    feed = Feed.objects.filter(name=feed_name)
    if feed:
        count = sendToFeed(feed, message)
        return HttpResponse("Sporočilo je poslano "+str(count)+ "X.")
    else:
        return HttpResponse("Ni takiga feeda")


#register on feed
def feed_register(person, message):
    print "register"
    feed_name = message#['message']['text'][1:]
    if feed_name in person.reg_feeds.all().values_list("name", flat=True):
        return feed_unregister(person, message)
        #return "message",  "Ti si ze registriran v obvestila: " + feed_name
    else:
        print("else")
        if feed_name in Feed.objects.all().values_list("name", flat=True):
            print("sdf")
            feed = Feed.objects.get(name=feed_name)
            person.reg_feeds.add(feed)
            return "message", "Uspesno si se registriral na obvestila: " + feed_name
        else:
            return "message", "Obvestilo: " + feed_name + " ne obstaja."


#Unregister from feed
def feed_unregister(person, message):
    print("unregister")
    feed_name = message#['message']['text'][1:]
    print( feed_name)
    print( person.reg_feeds.all().values_list("name", flat=True))
    if feed_name in person.reg_feeds.all().values_list("name", flat=True):
        feed = Feed.objects.get(name=feed_name)
        person.reg_feeds.remove(feed)
        return "message", "Uspesno smo te odjavili od obvestila: " + feed_name
    else:
        print("second")
        if feed_name in Feed.objects.all().values_list("name", flat=True):
            print("a")
            return "message",  "V ta obvestila nisi prijvlen"
        else:
            print("b")
            return "message",  "Obvestilo " + feed_name + " ne obstaja"


#Cron job method for sending reminders for events
def sendEventCron():
    for event in Events.objects.filter(startTime__lte=datetime.now(), sent=False):
        sendToFeed(event.feed, event.message)
        event.sent = True
        event.save()


def sendToFeed(feed, message):
    count = 0
    for person in Person.objects.filter(reg_feeds=feed):
        post_facebook_message(person.fb_id, message)
        count+=1
    return count


def getFeeds():
    return [feed.name for feed in Feed.objects.all()]

def getCardsKeywords():
    return [card.keyword for card in FbCard.objects.all()]