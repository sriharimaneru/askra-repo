from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^view(/?)(?P<profile_id>.*)$', 'userprofile.views.show_profile', name='viewprofile'),
    url(r'^edit(/)(?P<profile_id>.*)$', 'userprofile.views.edit_profile', name='editprofile'),
    url(r'^edit_basic(/?)(?P<profile_id>.*)$', 'userprofile.views.edit_profile_basic', name='editprofilebasic'),
    url(r'^edit_weblinks(/?)(?P<profile_id>.*)$', 'userprofile.views.edit_profile_weblinks', name='editprofileweblinks'),
    url(r'^edit_education(/?)(?P<profile_id>.*)$', 'userprofile.views.edit_profile_education', name='editprofileeducation'),
    url(r'^edit_employment(/?)(?P<profile_id>.*)$', 'userprofile.views.edit_profile_employment', name='editprofileemployment'),
    url(r'^reg-step-2(/?)$', 'userprofile.views.reg_step_2', name='regstep2'),
    url(r'^reg-step-3(/?)$', 'userprofile.views.reg_step_3', name='regstep3'),
    url(r'^bulk_upload(/?)$', 'userprofile.views.profile_bulk_upload', name='profilebulkupload'),
)
