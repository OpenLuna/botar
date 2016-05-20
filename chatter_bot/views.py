# -*- coding: UTF-8 -*-
from django.views.generic import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from pymongo import MongoClient
from bson.code import Code
from chatter_bot.models import ChatHistory, Location
from chatter_bot.utils import normalize_sentence
from  Levenshtein import distance
import random
from bot_content.utils import getPerson
from bot_content.views import feed_register, feed_unregister, getCardsKeywords, getFeeds
from bot_content.models import FbCard


dbClient = MongoClient('localhost', 27017)
learn=False
db = dbClient.bot_database

mapper = Code("""
    function(){
                        emit(this.request, 1);
                }
""")
reducer = Code("""
    function(key, value) { return null; }
""")


def parse(message, sender):
    response = get_response(sender, message)
    return response

    """if message[0] == "@":
        return feed_register(person, message)
    elif message[0] == "#":
        return feed_unregister(person, message)
    else:
        print "parse else"
        if FbCard.objects.filter(keyword=message.lower()):
            return "card", list(FbCard.objects.filter(keyword=message.lower()))
        else:
            print message"""
            


def get_response(fb_id, text):
    #print "finding", text
    mr = db.bot.map_reduce(mapper, reducer, out = {'inline' : 1}, full_response = True)
    keys = [item["_id"] for item in mr["results"]]

    ntext, isQuestion = normalize_sentence(text)

    #saving new paris if learn is ON
    if learn:
        if ChatHistory.objects.filter(fb_id=str(fb_id)) and list(ChatHistory.objects.filter(fb_id=str(fb_id)).order_by("id"))[-1].text == None:
            #print "Sharni " + text.decode("utf-8") + "za response od prejsnega"
            if ntext[0] == "x":
                ChatHistory(fb_id=str(fb_id), text="x", request=False).save()
                return "Če mi nočeš pomagat pa nič :("
            req = list(ChatHistory.objects.all().order_by("id"))[-2]
            pair = {"request":req.text, "response": text, "question": req.isQuestion}
            db.bot.insert_one(pair)
            ChatHistory(fb_id=str(fb_id), text=text, request=False).save()
            return "Zapomnil sem si tvoj predlog. Nadaljuj s pogovorm."
        elif text.lower()[:7] == "narobe:":
            text = text[8:]
            request_obj = list(ChatHistory.objects.filter(fb_id=str(fb_id), request=True).order_by("id"))[-1]
            print request_obj.text
            db_obj = db.bot.find_one({'request': request_obj.text})
            print db_obj
            pair = {"request":request_obj.text, "response": text, "question": request_obj.isQuestion}
            db.bot.replace_one(db_obj, pair)
            return "Hvala, da me poravljaš ;) s tabo bom postal močnejši"
        else:
            ChatHistory(fb_id=str(fb_id), text=" ".join(ntext), request=True, isQuestion=isQuestion).save()

    #find response
    if learn:
        if " ".join(ntext) in keys:
            resp = db.bot.find_one({'request': " ".join(ntext)})["response"]
            ChatHistory(fb_id=str(fb_id), text=resp, request=False).save()
            return resp
        else:
            ChatHistory(fb_id=str(fb_id), text=None, request=False).save()

            return "Na tvoj stavek se še ne znam odzivat. Predlagaj mi kaj naj rečem."
    else:
        print "Dists?"
        dists = distances(" ".join(ntext), keys)
        print dists
        min_dis = min(dists)
        mins = [i for i, v in enumerate(dists) if v == min_dis]
        print mins

        disfeed = distances(" ".join(ntext), getFeeds())
        print disfeed
        min_feed_d = min(disfeed)
        min_feed = [i for i, v in enumerate(disfeed) if v == min_feed_d]
        print min_feed

        discard = distances(" ".join(ntext), getCardsKeywords())
        print discard
        min_card_d = min(discard)
        min_card = [i for i, v in enumerate(discard) if v == min_card_d]
        print min_card

        o_min=min([min_dis, min_feed_d, min_card_d])
        print o_min
        type_of_resp = [i for i, v in zip(["message","feed","card"], [min_dis, min_feed_d, min_card_d]) if v == o_min]

        if text.lower()[:7] == "narobe:":
            print "narobe"
            return "message", correct(text, fb_id)
        else:
            ChatHistory(fb_id=str(fb_id), text=" ".join(ntext), request=True, isQuestion=isQuestion).save()
            if type_of_resp[0]=="message":
                resp = db.bot.find_one({'request': keys[random.choice(mins)]})["response"]
                ChatHistory(fb_id=str(fb_id), text=resp, request=False).save()
                return "message", resp
            elif type_of_resp[0]=="feed":
                return feed_register(getPerson(fb_id), getFeeds()[random.choice(min_feed)])
            elif type_of_resp[0]=="card":
                keyword = getCardsKeywords()[random.choice(min_card)]
                print "card send", keyword
                return "card", list(FbCard.objects.filter(keyword=keyword))


def distances(word, w_list):
    print word
    print w_list
    print "se najdem"
    return [distance(str(word), str(l_word)) for l_word in w_list]


def correct(text, fb_id):
    text = text[8:]
    request_obj = list(ChatHistory.objects.filter(fb_id=str(fb_id), request=True).order_by("id"))[-2]
    print request_obj.text
    db_obj = db.bot.find_one({'request': request_obj.text})
    print db_obj
    pair = {"request":request_obj.text, "response": text, "question": request_obj.isQuestion}
    print pair, type(pair)
    if db_obj:
        db.bot.replace_one(db_obj, pair)
    else:
        db.bot.insert_one(pair)
    return "Hvala, da me poravljaš ;) s tabo bom postal močnejši"