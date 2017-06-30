from django.conf.urls import url

from common import views

urlpatterns = [
    url(r'^$', views.home, name='home'),

    # override dbmailer api
    url(r'^dbmail/api/$', views.send_by_dbmail_custom, name='db-mail-api-custom'),
]
