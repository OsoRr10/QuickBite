from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.conf.urls.i18n import i18n_patterns
import django.conf.urls.i18n as i18n_urls

urlpatterns = [
    # URL para cambio de idioma (debe estar fuera de i18n_patterns)
    path('i18n/', include(i18n_urls)),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('api/', include('orders.urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    prefix_default_language=False,
)
