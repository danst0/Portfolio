from django.conf.urls import patterns, url

import core.views
import transactions.views

urlpatterns = patterns('',
                       url(r'^$', core.views.index, name='index'),
                       url(r'^update/$', core.views.update, name='update'),
                       url(r'^test/$', Transactions.views.test, name='test'),

                       # ex: /polls/5/
                       # url(r'^(?P<poll_id>\d+)/$', views.detail, name='detail'),
                       # ex: /polls/5/results/
                       #     url(r'^(?P<poll_id>\d+)/results/$', views.results, name='results'),
                       # ex: /polls/5/vote/
                       #     url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote'),
)

