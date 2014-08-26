from django.conf.urls import patterns, url

from core import views

urlpatterns = patterns('',
                       url(r'^/$', views.index, name='index'),
                       url(r'/update/$', views.update, name='update'),
                       url(r'/rolling_profitability', views.rolling_profitability, name='rolling_profitability'),
                       url(r'(?P<portfolio>[A-Z0-9a-z]+)/(?P<from_date>[0-9\-]+)/(?P<to_date>[0-9\-]+)/diagram.png$', views.rolling_profitability_png, name='rolling_profitabiliy_png'),

                       # ex: /polls/5/
                       # url(r'^(?P<poll_id>\d+)/$', views.detail, name='detail'),
                       # ex: /polls/5/results/
                       #     url(r'^(?P<poll_id>\d+)/results/$', views.results, name='results'),
                       # ex: /polls/5/vote/
                       #     url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote'),
)

