from django.conf.urls import patterns, include, url
from .views import sendMessageToFeed

urlpatterns = patterns('',
    url(r'^sendMessageToFeed/(?P<feed_name>[\w].+)/(?P<message>[\w].+)/', sendMessageToFeed),
)
