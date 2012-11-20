from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^servers/$', 'panini.cluster.views.servers'),
    url(r'^server/(?P<server_name>[\w\-]+)/install/(?P<role>[\w\-]+)/', 'panini.cluster.views.install'),
    url(r'^add-server/$', 'panini.cluster.views.add_server'),
    url(r'^delete-server/(?P<server_name>[\w\-]+)/(?P<server_id>[\w\-]+)?/$', 'panini.cluster.views.delete_server'),
)
