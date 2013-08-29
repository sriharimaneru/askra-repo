from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from askra.views import AboutView
from search.views import SearchView, SearchAjaxView

admin.autodiscover()

urlpatterns = patterns('',                    
    url(r'^about$', AboutView.as_view(), name='about'),
    url(r'^login$', TemplateView.as_view(template_name='login.html')),
    url(r'^logout$', auth_views.logout, {'next_page' : '/'},),
    url(r'^sign-up$', TemplateView.as_view(template_name='sign_up.html')),
    url(r'^searchajax/?$', SearchAjaxView.as_view(), name='haystack_search_ajax'),
    url(r'^profile/', include('userprofile.urls')),
     url(r'^admin/', include(admin.site.urls)),     
     url(r'^grappelli/', include('grappelli.urls')),
     url(r'', include('social_auth.urls')),
     url(r'', include('search.urls')),
     (r'^accounts/', include('registration.urls')),
)

urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))