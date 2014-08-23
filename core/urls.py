from django.conf.urls import patterns, url

from core import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'update$', views.update, name='update'),
                       url(r'rollingprofitability$', views.rolling_profitability, name='rolling_profitability'),


                       # ex: /polls/5/
                       # url(r'^(?P<poll_id>\d+)/$', views.detail, name='detail'),
                       # ex: /polls/5/results/
                       #     url(r'^(?P<poll_id>\d+)/results/$', views.results, name='results'),
                       # ex: /polls/5/vote/
                       #     url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote'),
)

