# Модели отображают информацию о данных, с которыми производится работа.
# Они содержат поля и поведение данных.
# Обычно одна модель представляет одну таблицу в базе данных.
# Каждая модель это класс унаследованный от django.db.models.Model.
# Атрибут модели представляет поле в базе данных.
# Django предоставляет автоматически созданное API для доступа к данным
from django.db import models
from django.utils.translation import gettext_lazy as _


# Категория товаров номенклатуры с поддержкой порядка сортировки и локализацией.
class Category(models.Model):
    name = models.CharField(_('Category name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    display_order = models.IntegerField(_('Display order'), default=0)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


# Карточка товара / номенклатурной единицы складского учета.
class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('Category')
    )
    sku = models.CharField(_('SKU / Article'), max_length=50, unique=True)
    barcode = models.CharField(_('Barcode'), max_length=100, unique=True, blank=True, null=True)
    name = models.CharField(_('Product name'), max_length=200)
    unit = models.CharField(_('Unit of measurement'), max_length=20, default='pcs')
    min_stock = models.DecimalField(_('Minimum stock balance'), max_digits=12, decimal_places=3, default=0)
    description = models.TextField(_('Description'), blank=True)
    image = models.ImageField(_('Product image'), upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(_('Is active status'), default=True)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['name']

    def __str__(self):
        return f"[{self.sku}] {self.name}"


# Топографическая ячейка адресации склада (Зона -> Стеллаж -> Ярус -> Ячейка).
class StorageLocation(models.Model):
    zone = models.CharField(_('Warehouse zone'), max_length=50)
    rack = models.CharField(_('Rack'), max_length=50)
    shelf = models.CharField(_('Shelf / Level'), max_length=50)
    cell = models.CharField(_('Cell / Position'), max_length=50)
    barcode = models.CharField(_('Location barcode'), max_length=100, unique=True, blank=True, null=True)

    class Meta:
        verbose_name = _('Storage location')
        verbose_name_plural = _('Storage locations')
        ordering = ['zone', 'rack', 'shelf', 'cell']
        unique_together = ('zone', 'rack', 'shelf', 'cell')

    def __str__(self):
        return f"{self.zone}-{self.rack}-{self.shelf}-{self.cell}"


# Физические остатки конкретного товара в конкретной складской ячейке.
class StockBalance(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='balances',
        verbose_name=_('Product')
    )
    location = models.ForeignKey(
        StorageLocation,
        on_delete=models.CASCADE,
        related_name='balances',
        verbose_name=_('Storage location')
    )
    quantity = models.DecimalField(_('Current quantity'), max_digits=12, decimal_places=3, default=0)

    class Meta:
        verbose_name = _('Stock balance')
        verbose_name_plural = _('Stock balances')
        unique_together = ('product', 'location')

    def __str__(self):
        return f"{self.product.name} @ {self.location}: {self.quantity} {self.product.unit}"