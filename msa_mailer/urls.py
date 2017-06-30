from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('common.urls')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^dbmail/', include('dbmail.urls')),
]
