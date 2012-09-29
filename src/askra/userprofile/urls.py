from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^view(/?)(?P<profile_id>.*)$', 'userprofile.views.show_profile', name='viewprofile'),
)
