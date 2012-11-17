from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'panini.views.home', name='home'),
    # url(r'^panini/', include('panini.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'panini.views.index'),
    url(r'^login/$', 'panini.views.login'),
    url(r'^logout/$', 'panini.views.logout'),
    url(r'^main/$', 'panini.views.main'),
)
