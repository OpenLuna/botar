# -*- coding: UTF-8 -*-
from .models import Person


def getPerson(sender):
    person = Person.objects.filter(fb_id=sender)
    if person:
        person = person[0]
    else:
        person = Person(fb_id=sender)
        person.save()

    return person
