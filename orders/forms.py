# Определение и настройка форм для валидации, обработки и стилизации вводимых пользователем данных.
# forms.py — Формы документооборота, контрагентов и табличной части
from django import forms
from django.utils.translation import gettext_lazy as _
from inventory.models import Product, StorageLocation
from .models import Contractor, DocumentItem, StockDocument


class ContractorForm(forms.ModelForm):
    """Форма для карточки контрагента (поставщик / покупатель)."""
    class Meta:
        model = Contractor
        fields = ['name', 'contractor_type', 'tax_id', 'phone', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contractor_type': forms.Select(attrs={'class': 'form-select'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234567890'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (707) 123-45-67'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class StockDocumentForm(forms.ModelForm):
    """Форма создания и редактирования шапки складского документа."""
    class Meta:
        model = StockDocument
        fields = ['doc_number', 'doc_type', 'contractor', 'comment']
        widgets = {
            'doc_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DOC-2026-0001'}),
            'doc_type': forms.Select(attrs={'class': 'form-select'}),
            'contractor': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class DocumentItemForm(forms.ModelForm):
    """Форма добавления товарной позиции в документ."""
    class Meta:
        model = DocumentItem
        fields = ['product', 'source_location', 'target_location', 'quantity', 'price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'source_location': forms.Select(attrs={'class': 'form-select'}),
            'target_location': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }