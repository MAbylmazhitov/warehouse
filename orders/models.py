# Модели отображают информацию о данных, с которыми производится работа.
# Они содержат поля и поведение данных.
# Обычно одна модель представляет одну таблицу в базе данных.
# Каждая модель это класс унаследованный от django.db.models.Model.
# Атрибут модели представляет поле в базе данных.
# Django предоставляет автоматически созданное API для доступа к данным
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from inventory.models import Product, StorageLocation


# Справочник контрагентов (Поставщики и Покупатели/Заказчики).
class Contractor(models.Model):
    TYPE_SUPPLIER = 'supplier'
    TYPE_CUSTOMER = 'customer'

    CONTRACTOR_TYPE_CHOICES = [
        (TYPE_SUPPLIER, _('Supplier')),
        (TYPE_CUSTOMER, _('Customer')),
    ]

    name = models.CharField(_('Contractor name / Legal entity'), max_length=200)
    contractor_type = models.CharField(
        _('Contractor type'),
        max_length=20,
        choices=CONTRACTOR_TYPE_CHOICES,
        default=TYPE_SUPPLIER
    )
    tax_id = models.CharField(_('Tax ID / INN'), max_length=20, blank=True)
    phone = models.CharField(_('Phone number'), max_length=50, blank=True)
    email = models.EmailField(_('Email address'), blank=True)
    address = models.TextField(_('Legal address'), blank=True)

    class Meta:
        verbose_name = _('Contractor')
        verbose_name_plural = _('Contractors')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_contractor_type_display()})"


# Шапка складского документа (Приход, Расход, Перемещение, Инвентаризация).
class StockDocument(models.Model):
    TYPE_INCOMING = 'incoming'      # Приходная накладная
    TYPE_OUTGOING = 'outgoing'      # Расходная накладная
    TYPE_TRANSFER = 'transfer'      # Внутрискладское перемещение
    TYPE_AUDIT = 'audit'            # Инвентаризация

    DOC_TYPE_CHOICES = [
        (TYPE_INCOMING, _('Receipt / Incoming')),
        (TYPE_OUTGOING, _('Expense / Outgoing')),
        (TYPE_TRANSFER, _('Internal Transfer')),
        (TYPE_AUDIT, _('Inventory Audit')),
    ]

    STATUS_DRAFT = 'draft'          # Черновик
    STATUS_CONDUCTED = 'conducted'  # Проведен
    STATUS_CANCELLED = 'cancelled'  # Отменен

    STATUS_CHOICES = [
        (STATUS_DRAFT, _('Draft')),
        (STATUS_CONDUCTED, _('Conducted')),
        (STATUS_CANCELLED, _('Cancelled')),
    ]

    doc_number = models.CharField(_('Document number'), max_length=50, unique=True)
    doc_type = models.CharField(_('Document type'), max_length=20, choices=DOC_TYPE_CHOICES)
    contractor = models.ForeignKey(
        Contractor,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='documents',
        verbose_name=_('Contractor')
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='stock_documents',
        verbose_name=_('Author / Responsible user')
    )
    doc_date = models.DateTimeField(_('Document date'), auto_now_add=True)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    comment = models.TextField(_('Comment'), blank=True)

    class Meta:
        verbose_name = _('Stock document')
        verbose_name_plural = _('Stock documents')
        ordering = ['-doc_date']

    def __str__(self):
        return f"№{self.doc_number} ({self.get_doc_type_display()}) — {self.get_status_display()}"


# Табличная часть складского документа (Товарные позиции, количество и ячейки).
class DocumentItem(models.Model):
    document = models.ForeignKey(
        StockDocument,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Document')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='document_items',
        verbose_name=_('Product')
    )
    source_location = models.ForeignKey(
        StorageLocation,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='source_document_items',
        verbose_name=_('Source location (From)')
    )
    target_location = models.ForeignKey(
        StorageLocation,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='target_document_items',
        verbose_name=_('Target location (To)')
    )
    quantity = models.DecimalField(_('Quantity'), max_digits=12, decimal_places=3)
    price = models.DecimalField(_('Unit price'), max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = _('Document item')
        verbose_name_plural = _('Document items')

    def __str__(self):
        return f"{self.product.name} x {self.quantity} ({self.document.doc_number})"


# Акт расхождений / Инвентаризационная ведомость.
class InventoryAudit(models.Model):
    document = models.ForeignKey(
        StockDocument,
        on_delete=models.CASCADE,
        related_name='audits',
        verbose_name=_('Audit document')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='inventory_audits',
        verbose_name=_('Product')
    )
    location = models.ForeignKey(
        StorageLocation,
        on_delete=models.PROTECT,
        related_name='inventory_audits',
        verbose_name=_('Storage location')
    )
    accounting_quantity = models.DecimalField(_('Accounting quantity'), max_digits=12, decimal_places=3)
    actual_quantity = models.DecimalField(_('Actual quantity'), max_digits=12, decimal_places=3)
    difference = models.DecimalField(_('Difference (Actual - Accounting)'), max_digits=12, decimal_places=3)

    class Meta:
        verbose_name = _('Inventory audit entry')
        verbose_name_plural = _('Inventory audit entries')

    def __str__(self):
        return f"{self.product.name} @ {self.location}: Diff = {self.difference}"