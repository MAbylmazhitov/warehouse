# Представления приложения складского учета (inventory) для обработки HTTP-запросов, реализации
# бизнес-логики, управления правами доступа (Storekeeper / Manager) и связывания моделей с шаблонами.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Sum, Count, Q
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import CategoryForm, ProductForm, StorageLocationForm
from .mixins import ManagerRequiredMixin, StorekeeperRequiredMixin
from .models import Category, Product, StockBalance, StorageLocation


# Общий каталог номенклатуры (товаров) со списком остатков и поисковым контекстом.
# Общий каталог номенклатуры (товаров) со списком остатков и поисковым контекстом.
def product_list(request):
    products = Product.objects.select_related('category').filter(is_active=True)
    categories = Category.objects.all()

    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query) |
            Q(barcode__icontains=query) |
            Q(category__name__icontains=query)
        )

    context = {
        'products': products,
        'categories': categories,
        'search_query': query or '',
    }
    return render(request, 'inventory/product_list.html', context)


# Карточка номенклатурной единицы с детальной информацией, минимальными остатками и наличием по ячейкам склада.
def product_details(request, id):
    product = get_object_or_404(Product, id=id)

    # Текущие остатки по конкретным ячейкам хранения
    balances = StockBalance.objects.filter(product=product).select_related('location')

    # Суммарное количество товара на складе
    total_quantity = balances.aggregate(total=Sum('quantity'))['total'] or 0

    context = {
        'product': product,
        'balances': balances,
        'total_quantity': total_quantity,
        'is_low_stock': total_quantity <= product.min_stock,
    }
    return render(request, 'inventory/product_details.html', context)

# Сводная ведомость остатков товаров по ячейкам склада
def stock_balance_list(request):
    balances = StockBalance.objects.select_related('product', 'location', 'product__category').filter(quantity__gt=0)
    
    query = request.GET.get('q')
    if query:
        balances = balances.filter(
            Q(product__name__icontains=query) |
            Q(product__sku__icontains=query) |
            Q(location__zone__icontains=query) |
            Q(location__barcode__icontains=query)
        )

    context = {
        'balances': balances,
        'search_query': query or '',
    }
    return render(request, 'inventory/stock_balance_list.html', context)
    
# --- УПРАВЛЕНИЕ КАТЕГОРИЯМИ ---

# Панель менеджера для просмотра списка категорий номенклатуры.
class CategoryManageListView(ManagerRequiredMixin, ListView):
    model = Category
    template_name = 'inventory/manage/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        queryset = Category.objects.annotate(products_count=Count('products'))
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


# Создание новой категории номенклатуры.
class CategoryCreateView(ManagerRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/manage/category_form.html'
    success_url = reverse_lazy('inventory:manage_category_list')


# Редактирование существующей категории номенклатуры.
class CategoryUpdateView(ManagerRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/manage/category_form.html'
    success_url = reverse_lazy('inventory:manage_category_list')

# Удаление категории
class CategoryDeleteView(ManagerRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('inventory:manage_category_list')

# --- УПРАВЛЕНИЕ НОМЕНКЛАТУРОЙ (ТОВАРАМИ) ---

# Добавление нового товара в номенклатуру склада (доступно кладовщикам и менеджерам).
class ProductCreateView(StorekeeperRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/manage/product_form.html'
    success_url = reverse_lazy('inventory:product_list')


# Изменение параметров карточки товара (артикул, наименование, минимальный остаток).
class ProductUpdateView(StorekeeperRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/manage/product_form.html'
    success_url = reverse_lazy('inventory:product_list')


# Деактивация / удаление позиции номенклатуры (только менеджер).
class ProductDeleteView(ManagerRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('inventory:product_list')

# --- УПРАВЛЕНИЕ СТОРАДЖ-ЯЧЕЙКАМИ (ТОПОЛОГИЯ СКЛАДА) ---

# Просмотр топографии склада и адресных ячеек.
class StorageLocationListView(StorekeeperRequiredMixin, ListView):
    model = StorageLocation
    template_name = 'inventory/manage/location_list.html'
    context_object_name = 'locations'

    def get_queryset(self):
        queryset = StorageLocation.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(zone__icontains=query) |
                Q(rack__icontains=query) |
                Q(shelf__icontains=query) |
                Q(cell__icontains=query) |
                Q(barcode__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


# Добавление новой ячейки хранения (Зона-Стеллаж-Ярус-Ячейка).
class StorageLocationCreateView(ManagerRequiredMixin, CreateView):
    model = StorageLocation
    form_class = StorageLocationForm
    template_name = 'inventory/manage/location_form.html'
    success_url = reverse_lazy('inventory:location_list')


# Редактирование адресации/штрихкода ячейки.
class StorageLocationUpdateView(ManagerRequiredManagerRequiredMixin if False else ManagerRequiredMixin, UpdateView): # оставьте свой ManagerRequiredMixin
    model = StorageLocation
    form_class = StorageLocationForm
    template_name = 'inventory/manage/location_form.html'
    success_url = reverse_lazy('inventory:location_list')
    
# Удаление ячейки хранения (через модальное окно)
class StorageLocationDeleteView(ManagerRequiredMixin, DeleteView):
    model = StorageLocation
    success_url = reverse_lazy('inventory:location_list')  