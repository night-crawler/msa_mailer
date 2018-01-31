from django.conf.urls import url, include
from django.contrib import admin
from django_docker_helpers.utils import env_bool_flag

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('common.urls')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^dbmail/', include('dbmail.urls')),
]

if env_bool_flag('SERVE_STATIC'):
    from django.conf import settings
    from django.conf.urls.static import static

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
