from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('',
                       
    url(r'^$', 'userprofile.views.search', name='haystack_search'),
    url(r'^about$', 'askra.views.about', name='about'),
    url(r'^login$', direct_to_template, {'template' : 'login.html'},),
    url(r'^logout$', auth_views.logout, {'next_page' : '/'},),
    url(r'^sign-up$', direct_to_template, {'template' : 'sign_up.html'},),
    url(r'^profile/', include('userprofile.urls')),
    
#    url(r'^index$', 'askra.views.index', name='index'), #temporarily. Will remove this @srihari
#    url(r'^view_profile$', TemplateView.as_view(template_name='view_profile.html'), name='view_profile'),    
#    url(r'^reg-step-2$', TemplateView.as_view(template_name='reg-step-2.html'), name='reg-2'),  
#    url(r'^reg-step-3$', TemplateView.as_view(template_name='reg-step-3.html'), name='reg-3'),
#    url(r'^ajaxsearch', 'userprofile.views.ajaxresponse', name='ajax_search'),
#    url(r'^ajaxtest', 'userprofile.views.ajaxtest', ),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

     url(r'^admin/', include(admin.site.urls)),     
     url(r'^grappelli/', include('grappelli.urls')),
     url(r'', include('social_auth.urls')),
     (r'^accounts/', include('registration.urls')),
)

urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))