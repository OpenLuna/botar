from django.conf.urls import patterns, include, url
from .views import sendMessageToId, Botw

urlpatterns = patterns('',
    #url(r'^bot/?$',bot),
    url(r'^bot/?$', Botw.as_view()),
    url(r'^sendMessageToId/(?P<fb_id>\d+)/(?P<message>[\w].+)/', sendMessageToId),
)
