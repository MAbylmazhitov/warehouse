# Маршрутизатор URL приложения inventory для обработки запросов, связывания эндпоинтов
# с представлениями и организации внутренней навигации складского модуля.
from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
       
    # Каталог и остатки
    path('', views.product_list, name='product_list'),
    path('product/<int:id>/', views.product_details, name='product_details'),
    path('balances/', views.stock_balance_list, name='stock_balance_list'),

    # Категории
    path('manage/categories/', views.CategoryManageListView.as_view(), name='manage_category_list'),
    path('manage/categories/add/', views.CategoryCreateView.as_view(), name='category_create'),
    path('manage/categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('manage/categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Номенклатура
    path('manage/products/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('manage/products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('manage/products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

    # Топология склада
    path('locations/', views.StorageLocationListView.as_view(), name='location_list'),
    path('locations/add/', views.StorageLocationCreateView.as_view(), name='location_create'),
    path('locations/<int:pk>/edit/', views.StorageLocationUpdateView.as_view(), name='location_update'),
    path('locations/<int:pk>/delete/', views.StorageLocationDeleteView.as_view(), name='location_delete'),
]