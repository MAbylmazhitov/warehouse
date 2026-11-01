# Определение и настройка форм для валидации, обработки и стилизации вводимых пользователем данных.
# forms.py — Формы для управления номенклатурой, категориями и ячейками склада
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Category, Product, StorageLocation


class CategoryForm(forms.ModelForm):
    """Форма для создания и редактирования категорий товаров."""
    class Meta:
        model = Category
        fields = ['name', 'description', 'display_order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('e.g., Fasteners, Electronics')}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ProductForm(forms.ModelForm):
    """Форма для добавления и обновления карточки номенклатурной единицы."""
    class Meta:
        model = Product
        fields = ['category', 'sku', 'barcode', 'name', 'unit', 'min_stock', 'description', 'image', 'is_active']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SKU-100234'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '4601234567890'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('pcs, kg, m')}),
            'min_stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class StorageLocationForm(forms.ModelForm):
    """Форма для настройки топологии склада (адресные ячейки)."""
    class Meta:
        model = StorageLocation
        fields = ['zone', 'rack', 'shelf', 'cell', 'barcode']
        widgets = {
            'zone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('e.g., Zone A')}),
            'rack': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('e.g., R-01')}),
            'shelf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('e.g., S-03')}),
            'cell': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('e.g., C-12')}),
            'barcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'LOC-A-01-03-12'}),
        }