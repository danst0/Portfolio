from django.conf.urls import patterns, url

from core import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'import_historic_quotes/', views.import_historic_quotes, name='import_historic_quotes'),
                       url(r'import_all/', views.import_all, name='import_all'),
                       url(r'import_cortalconsors_quotes/', views.import_cortalconsors_quotes, name='import_cortalconsors_quotes'),
                       url(r'update_pdfs/', views.update_pdfs, name='update_pdfs'),
                       url(r'import_quotes/', views.update_stocks_boerse_frankfurt, name='update_stocks_boerse_frankfurt'),
                       url(r'import_outbank/', views.import_outbank, name='import_outbank'),
                       url(r'new_invest/', views.new_invest, name='new_invest'),
                       url(r'rolling_profitability/', views.rolling_profitability, name='rolling_profitability'),
                       url(r'portfolio_development/',
                           views.portfolio_development,
                           name='portfolio_development'),
                       url(r'portfolio_overview/',
                           views.portfolio_overview,
                           name='portfolio_overview'),
                       url(r'stock_graph/', views.stock_graph, name='stock_graph'),
                       url(r'(?P<security>.+)/(?P<from_date>[0-9\-]+)/(?P<to_date>[0-9\-]+)/stock_graph_diagram.png$',
                           views.stock_graph_png,
                           name='stock_graph_png'),
                       url(r'forecast_retirement/', views.forecast_retirement, name='forecast_retirement'),
                       # ex: /polls/5/
                       # url(r'^(?P<poll_id>\d+)/$', views.detail, name='detail'),
                       # ex: /polls/5/results/
                       #     url(r'^(?P<poll_id>\d+)/results/$', views.results, name='results'),
                       # ex: /polls/5/vote/
                       #     url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote'),
)

