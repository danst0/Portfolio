from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import RedirectView

admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       url(r'^$', RedirectView.as_view(pattern_name='new_invest')),
                       # url(r'^blog/', include('blog.urls')),
                       url(r'^core/', include('core.urls')),
                       url(r'^import/', include('importer.urls')),

                       url(r'^transactions/', include('transactions.urls')),
                       url(r'^admin/', include(admin.site.urls), name='admin'),
                       url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
                       url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', name='logout'),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

