from django.contrib import admin
from .models import Contractor, StockDocument, DocumentItem, InventoryAudit


class DocumentItemInline(admin.TabularInline):
    model = DocumentItem
    extra = 1


class InventoryAuditInline(admin.TabularInline):
    model = InventoryAudit
    extra = 1


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contractor_type', 'tax_id', 'phone', 'email')
    list_filter = ('contractor_type',)
    search_fields = ('name', 'tax_id', 'phone', 'email')


@admin.register(StockDocument)
class StockDocumentAdmin(admin.ModelAdmin):
    list_display = ('doc_number', 'doc_type', 'contractor', 'author', 'doc_date', 'status')
    list_filter = ('doc_type', 'status', 'doc_date')
    search_fields = ('doc_number', 'comment')
    inlines = [DocumentItemInline, InventoryAuditInline]


@admin.register(DocumentItem)
class DocumentItemAdmin(admin.ModelAdmin):
    list_display = ('document', 'product', 'quantity', 'price', 'source_location', 'target_location')
    list_filter = ('document__doc_type',)
    search_fields = ('document__doc_number', 'product__name')


@admin.register(InventoryAudit)
class InventoryAuditAdmin(admin.ModelAdmin):
    list_display = ('document', 'product', 'location', 'accounting_quantity', 'actual_quantity', 'difference')
    list_filter = ('location__zone',)
    search_fields = ('document__doc_number', 'product__name')