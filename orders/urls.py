# Маршрутизатор URL приложения orders для обработки запросов документооборота,
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Контрагенты
    path('contractors/', views.ContractorListView.as_view(), name='contractor_list'),
    path('contractors/add/', views.ContractorCreateView.as_view(), name='contractor_create'),
    path('contractors/<int:pk>/edit/', views.ContractorUpdateView.as_view(), name='contractor_update'),
    path('contractor/<int:pk>/delete/', views.ContractorDeleteView.as_view(), name='contractor_delete'),
    
    # Журнал документов
    path('documents/', views.StockDocumentListView.as_view(), name='document_list'),
    path('documents/create/', views.StockDocumentCreateView.as_view(), name='document_create'),
    path('documents/<int:pk>/', views.StockDocumentDetailView.as_view(), name='document_detail'),
    path('documents/<int:pk>/edit/', views.StockDocumentUpdateView.as_view(), name='document_update'),

    # Проведение и отмена
    path('documents/<int:pk>/conduct/', views.conduct_document, name='document_conduct'),
    path('documents/<int:pk>/cancel/', views.cancel_document, name='document_cancel'),

    # Позиции документов
    path('documents/<int:doc_pk>/items/add/', views.document_item_create, name='document_item_create'),
    path('items/<int:pk>/delete/', views.document_item_delete, name='document_item_delete'),
    
    # Отчеты
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
]