# Представления приложения документооборота и движения МЦ (orders)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView
from django.db.models import Q

from inventory.mixins import ManagerRequiredMixin, StorekeeperRequiredMixin
from inventory.models import StockBalance, Category
from .forms import ContractorForm, DocumentItemForm, StockDocumentForm
from .models import Contractor, DocumentItem, StockDocument
from .reports import get_stock_balance_report, get_document_movement_report, get_low_stock_report


# --- УПРАВЛЕНИЕ КОНТРАГЕНТАМИ ---

class ContractorListView(StorekeeperRequiredMixin, ListView):
    model = Contractor
    template_name = 'orders/contractor_list.html'
    context_object_name = 'contractors'

    def get_queryset(self):
        queryset = Contractor.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(tax_id__icontains=query) |
                Q(phone__icontains=query) |
                Q(email__icontains=query) |
                Q(address__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class ContractorCreateView(ManagerRequiredMixin, CreateView):
    model = Contractor
    form_class = ContractorForm
    template_name = 'orders/contractor_form.html'
    success_url = reverse_lazy('orders:contractor_list')


class ContractorUpdateView(ManagerRequiredMixin, UpdateView):
    model = Contractor
    form_class = ContractorForm
    template_name = 'orders/contractor_form.html'
    success_url = reverse_lazy('orders:contractor_list')


# Добавляем класс удаления контрагента (доступен только менеджерам)
class ContractorDeleteView(ManagerRequiredMixin, DeleteView):
    model = Contractor
    success_url = reverse_lazy('orders:contractor_list')


# --- СКЛАДСКИЕ ДОКУМЕНТЫ ---

class StockDocumentListView(StorekeeperRequiredMixin, ListView):
    model = StockDocument
    template_name = 'orders/document_list.html'
    context_object_name = 'documents'
    paginate_by = 20

    def get_queryset(self):
        queryset = StockDocument.objects.select_related('contractor', 'author').all().order_by('-doc_date')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(doc_number__icontains=query) |
                Q(contractor__name__icontains=query) |
                Q(doc_type__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

class StockDocumentDetailView(StorekeeperRequiredMixin, DetailView):
    model = StockDocument
    template_name = 'orders/document_detail.html'
    context_object_name = 'document'


class StockDocumentCreateView(StorekeeperRequiredMixin, CreateView):
    model = StockDocument
    form_class = StockDocumentForm
    template_name = 'orders/document_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('orders:document_detail', kwargs={'pk': self.object.pk})


class StockDocumentUpdateView(StorekeeperRequiredMixin, UpdateView):
    model = StockDocument
    form_class = StockDocumentForm
    template_name = 'orders/document_form.html'

    def dispatch(self, request, *args, **kwargs):
        doc = self.get_object()
        if doc.status != StockDocument.STATUS_DRAFT:
            messages.error(request, _('Conducted or cancelled documents cannot be edited.'))
            return redirect('orders:document_detail', pk=doc.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('orders:document_detail', kwargs={'pk': self.object.pk})


# --- ПРОВЕДЕНИЕ И ОТМЕНА ДОКУМЕНТОВ ---

@transaction.atomic
def conduct_document(request, pk):
    document = get_object_or_404(StockDocument, pk=pk)

    if document.status != StockDocument.STATUS_DRAFT:
        messages.warning(request, _('Only draft documents can be conducted.'))
        return redirect('orders:document_detail', pk=pk)

    if not document.items.exists():
        messages.error(request, _('Cannot conduct an empty document without items.'))
        return redirect('orders:document_detail', pk=pk)

    for item in document.items.all():
        if document.doc_type == StockDocument.TYPE_INCOMING:
            if not item.target_location:
                messages.error(request, _('Target location is required for incoming document.'))
                return redirect('orders:document_detail', pk=pk)
            balance, created = StockBalance.objects.get_or_create(
                product=item.product,
                location=item.target_location,
                defaults={'quantity': 0}
            )
            balance.quantity += item.quantity
            balance.save()

        elif document.doc_type == StockDocument.TYPE_OUTGOING:
            if not item.source_location:
                messages.error(request, _('Source location is required for outgoing document.'))
                return redirect('orders:document_detail', pk=pk)
            balance = StockBalance.objects.filter(
                product=item.product,
                location=item.source_location
            ).first()
            if not balance or balance.quantity < item.quantity:
                messages.error(request, _('Insufficient stock for product "%(product)s".') % {'product': item.product.name})
                return redirect('orders:document_detail', pk=pk)
            balance.quantity -= item.quantity
            balance.save()

        elif document.doc_type == StockDocument.TYPE_TRANSFER:
            if not item.source_location or not item.target_location:
                messages.error(request, _('Source and Target locations are required for transfer.'))
                return redirect('orders:document_detail', pk=pk)
            src_balance = StockBalance.objects.filter(
                product=item.product,
                location=item.source_location
            ).first()
            if not src_balance or src_balance.quantity < item.quantity:
                messages.error(request, _('Insufficient stock for transfer of "%(product)s".') % {'product': item.product.name})
                return redirect('orders:document_detail', pk=pk)
            src_balance.quantity -= item.quantity
            src_balance.save()

            tgt_balance, created = StockBalance.objects.get_or_create(
                product=item.product,
                location=item.target_location,
                defaults={'quantity': 0}
            )
            tgt_balance.quantity += item.quantity
            tgt_balance.save()

    document.status = StockDocument.STATUS_CONDUCTED
    document.save()
    messages.success(request, _('Document №%(number)s successfully conducted.') % {'number': document.doc_number})
    return redirect('orders:document_detail', pk=pk)


def cancel_document(request, pk):
    document = get_object_or_404(StockDocument, pk=pk)

    if document.status != StockDocument.STATUS_CONDUCTED:
        messages.warning(request, _('Only conducted documents can be cancelled.'))
        return redirect('orders:document_detail', pk=pk)

    document.status = StockDocument.STATUS_CANCELLED
    document.save()
    messages.info(request, _('Document №%(number)s has been cancelled.') % {'number': document.doc_number})
    return redirect('orders:document_detail', pk=pk)


# --- ПОЗИЦИИ ДОКУМЕНТА ---

def document_item_create(request, doc_pk):
    document = get_object_or_404(StockDocument, pk=doc_pk)

    if document.status != StockDocument.STATUS_DRAFT:
        messages.error(request, _('Cannot add items to a conducted document.'))
        return redirect('orders:document_detail', pk=doc_pk)

    if request.method == 'POST':
        form = DocumentItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.document = document
            item.save()
            return redirect('orders:document_detail', pk=doc_pk)
    else:
        form = DocumentItemForm()

    return render(request, 'orders/document_item_form.html', {'form': form, 'document': document})


def document_item_delete(request, pk):
    item = get_object_or_404(DocumentItem, pk=pk)
    doc_pk = item.document.pk

    if item.document.status == StockDocument.STATUS_DRAFT:
        item.delete()
        messages.success(request, _('Item removed from document.'))
    else:
        messages.error(request, _('Cannot delete items from a conducted document.'))

    return redirect('orders:document_detail', pk=doc_pk)
    
@login_required
def reports_dashboard(request):
    """Единая панель отчётов WMS"""
    report_type = request.GET.get('report_type', 'balances')
    
    # Общие фильтры
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    category_id = request.GET.get('category')
    doc_type = request.GET.get('doc_type')
    contractor_id = request.GET.get('contractor')
    query = request.GET.get('q')
    
    context = {
        'report_type': report_type,
        'categories': Category.objects.all(),
        'contractors': Contractor.objects.all(),
        'search_query': query or '',
        'date_from': date_from or '',
        'date_to': date_to or '',
        'selected_category': category_id or '',
        'selected_doc_type': doc_type or '',
        'selected_contractor': contractor_id or '',
    }
    
    # Генерация данных в зависимости от выбранного типа отчёта
    if report_type == 'balances':
        context['report_data'] = get_stock_balance_report(category_id=category_id, query=query)
    elif report_type == 'movements':
        context['report_data'] = get_document_movement_report(
            date_from=date_from, date_to=date_to, doc_type=doc_type, contractor_id=contractor_id
        )
    elif report_type == 'low_stock':
        context['report_data'] = get_low_stock_report()
        
    return render(request, 'orders/reports_dashboard.html', context)