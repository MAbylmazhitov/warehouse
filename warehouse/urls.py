# urls.py — Главный маршрутизатор URL проекта WMS Control для централизованной координации маршрутов приложений.
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from accounts import views as accounts_views

# Маршруты без языковых префиксов
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]

# Маршруты с поддержкой многоязычности (i18n: EN/RU)
urlpatterns += i18n_patterns(
    # --- ИНФОРМАЦИОННЫЕ И ИСПОЛНИТЕЛЬНЫЕ СТРАНИЦЫ ---
    path('', accounts_views.index, name='index'),
    path('about/', accounts_views.about, name='about'),
    path('contact/', accounts_views.contact, name='contact'),

    # --- АВТОРИЗАЦИЯ И ПРОФИЛЬ СОТРУДНИКА (accounts) ---
    path('account/', include('accounts.urls', namespace='accounts')),
    # Алиасы для прямого перехода к авторизации/регистрации
    path('register/', accounts_views.register_view, name='register'),
    path('auth/', include('django.contrib.auth.urls')),

    # --- СКЛАДСКОЙ УЧЕТ И НОМЕНКЛАТУРА (inventory) ---
    path('inventory/', include('inventory.urls', namespace='inventory')),

    # --- НАКЛАДНЫЕ И ДОКУМЕНТЫ ДВИЖЕНИЯ (orders) ---
    path('orders/', include('orders.urls', namespace='orders')),

    prefix_default_language=False
)

# Подключение раздачи медиафайлов (аватары, штрихкоды, схемы) в режиме разработки (DEBUG = True).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)