'''
Created on 17-Aug-2013

@author: srihari
'''
from django.conf.urls import patterns, url
from .views import SearchAjaxView, ProfileSearchView
from .forms import CustomSearchForm


urlpatterns = patterns('',
                       url(r'^$', ProfileSearchView(form_class=CustomSearchForm, template="search/search.html",
                                                    load_all=False), name='haystack_search_test'),
                       #    url(r'^searchajax/?$', SearchAjaxView.as_view(), name='haystack_search_ajax'),
                       )
