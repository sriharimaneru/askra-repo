from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.generic import TemplateView


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'askra.views.index', name='home'),
    url(r'^profile/', include('userprofile.urls')),
    url(r'^index$', 'askra.views.index', name='index'), #temporarily. Will remove this @srihari
    url(r'^view_profile$', TemplateView.as_view(template_name='view_profile.html'), name='view_profile'),    
    url(r'^reg-step-2$', TemplateView.as_view(template_name='reg-step-2.html'), name='reg-2'),  
    url(r'^reg-step-3$', TemplateView.as_view(template_name='reg-step-3.html'), name='reg-3'),
    url(r'^search', 'userprofile.views.search', name='haystack_search'),
    url(r'^ajaxsearch', 'userprofile.views.ajaxresponse', name='ajax_search'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

     #Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
     
     url(r'^grappelli/', include('grappelli.urls')),

)

urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))

