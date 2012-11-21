from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^launch/$', 'panini.mapreduce.views.launch'),
)
