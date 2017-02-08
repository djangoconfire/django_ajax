"""analytics URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.conf import settings

urlpatterns = [
    url(r'^suggest/',include('suggest.urls',namespace='suggest')),
    url(r'^admin/', admin.site.urls),
    #url(r'^o/',include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'ajax/',include('suggest.urls',namespace='ajax')),
    #url('socialauth/', include('social.apps.django_app.urls', namespace='social')), 
    url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    #url(r'^tinymce/', include('tinymce.urls')),
    
    #For testing
    url(r'^testing/',include('suggest.urls',namespace='testing')),
]

urlpatterns +=[
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
]
