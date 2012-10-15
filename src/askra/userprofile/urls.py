from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^view(/?)(?P<profile_id>.*)$', 'userprofile.views.show_profile', name='viewprofile'),
    url(r'^edit(/)(?P<profile_id>.*)$', 'userprofile.views.edit_profile_basic', name='editprofilebasic'),
    url(r'^edit_basic(/?)(?P<profile_id>.*)$', 'userprofile.views.edit_profile_basic', name='editprofilebasic'),
    url(r'^edit_weblinks(/?)(?P<profile_id>.*)$', 'userprofile.views.edit_profile_weblinks', name='editprofileweblinks'),
    url(r'^edit_education(/?)(?P<profile_id>.*)$', 'userprofile.views.edit_profile_education', name='editprofileeducation'),
    url(r'^edit_employment(/?)(?P<profile_id>.*)$', 'userprofile.views.edit_profile_employment', name='editprofileemployment'),
)