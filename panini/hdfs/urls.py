from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^show(?P<path>/(?:[\w\-\.]*/)*)$', 'panini.hdfs.views.show'),
    url(r'^mkdir(?P<path>/(?:[\w\-\.]*/)*)$', 'panini.hdfs.views.mkdir'),
    url(r'^put(?P<path>/(?:[\w\-\.]*/)*)$', 'panini.hdfs.views.put'),
    url(r'^delete(?P<path>/(?:[\w\-\.]*/)*)$', 'panini.hdfs.views.delete'),
)
