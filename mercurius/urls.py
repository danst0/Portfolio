from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mercurius.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^m2', include('core.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

