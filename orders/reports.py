from django.db.models import Sum, Q
from inventory.models import StockBalance, Product
from .models import StockDocument, DocumentItem

def get_stock_balance_report(category_id=None, query=None):
    """Отчёт по текущим остаткам товаров на складе"""
    balances = StockBalance.objects.select_related('product', 'location', 'product__category').filter(quantity__gt=0)
    
    if category_id:
        balances = balances.filter(product__category_id=category_id)
        
    if query:
        balances = balances.filter(
            Q(product__name__icontains=query) |
            Q(product__sku__icontains=query) |
            Q(location__zone__icontains=query) |
            Q(location__barcode__icontains=query)
        )
    return balances


def get_document_movement_report(date_from=None, date_to=None, doc_type=None, contractor_id=None):
    """Отчёт по движению складских документов за период"""
    documents = StockDocument.objects.select_related('contractor', 'author').all().order_by('-doc_date')
    
    if date_from:
        documents = documents.filter(doc_date__gte=date_from)
    if date_to:
        documents = documents.filter(doc_date__lte=date_to)
    if doc_type:
        documents = documents.filter(doc_type=doc_type)
    if contractor_id:
        documents = documents.filter(contractor_id=contractor_id)
        
    return documents


def get_low_stock_report():
    """Отчёт по товарам с критическим / низким остатком"""
    # Собираем все активные товары и считаем их суммарный остаток
    products = Product.objects.filter(is_active=True).select_related('category')
    low_stock_items = []
    
    for product in products:
        total_qty = StockBalance.objects.filter(product=product).aggregate(total=Sum('quantity'))['total'] or 0
        if total_qty <= product.min_stock:
            low_stock_items.append({
                'product': product,
                'total_quantity': total_qty,
                'min_stock': product.min_stock,
            })
            
    return low_stock_items