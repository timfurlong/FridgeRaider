from django.conf.urls import patterns, url
from FridgeRaiderProject.settings import useSimpleSearch
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('FridgeRaider.views',
    # Examples:
    url(r'^$', 'home', name='home'),
    url(r'^about/$', 'about',),
    # url(r'^search/$', 'search',name='search'),
    # url(r'^FridgeRaiderProject/', include('FridgeRaiderProject.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

if useSimpleSearch:
  urlpatterns += patterns('FridgeRaider.views',
    url(r'^search/$', 'searchSimple',),
    url(r'^search/(?P<page>\d+)/$', 'searchSimple',name='search'),)
else:
  urlpatterns += patterns('FridgeRaider.views',
    url(r'^search/$', 'search',),
    url(r'^search/(?P<page>\d+)/$', 'search',name='search'),)

'''
urlpatterns = patterns('',
   # Examples:
   # url(r'^$', 'mysite.views.home', name='home'),
   # url(r'^mysite/', include('mysite.foo.urls')),

   # Uncomment the admin/doc line below to enable admin documentation:
   # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

   url(r'^polls/$', 'polls.views.index'),
   url(r'^polls/(?P<poll_id>\d+)/$', 'polls.views.detail'),
   url(r'^polls/(?P<poll_id>\d+)/results/$', 'polls.views.results'),
   url(r'^polls/(?P<poll_id>\d+)/vote/$', 'polls.views.vote'),

   # Uncomment the next line to enable the admin:
   url(r'^admin/', include(admin.site.urls)),
)
'''