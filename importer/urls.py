from . import views


from django.conf.urls import patterns, url

urlpatterns = patterns('importer.views',
    url(r'^list/$', 'list', name='list'),
)
