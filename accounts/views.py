# views.py — Представления приложения accounts для системы автоматизации складского учета (WMS)
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from inventory.mixins import ManagerRequiredMixin
from inventory.models import Product
from orders.models import Contractor, StockDocument
from .forms import CustomUserCreationForm, UserUpdateForm, WarehouseProfileForm
from .models import Profile

User = get_user_model()


# Главная страница WMS-системы (Дашборд с метриками склада)
def index(request):
    total_products = Product.objects.filter(is_active=True).count()
    total_documents = StockDocument.objects.count()
    total_contractors = Contractor.objects.count()

    context = {
        'total_products': total_products,
        'total_documents': total_documents,
        'total_contractors': total_contractors,
    }
    return render(request, "index.html", context)


# Страница «О системе / О складе»
def about(request):
    return render(request, "about.html")


# Страница «Контакты и логистический хаб»
def contact(request):
    return render(request, "contact.html")


# Обработка регистрации новых пользователей с автоматическим входом
def register_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                _("Account created successfully. Welcome to WMS Control!"),
            )
            return redirect("index")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


# Альтернативный эндпоинт регистрации пользователей со стандартной формой Django
def signup(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                _("Account created successfully. Welcome to WMS Control!"),
            )
            return redirect('index')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})


# Завершение сеанса текущего пользователя
def logoutUser(request):
    logout(request)
    return redirect("index")


# Просмотр и редактирование профиля текущего сотрудника
@login_required
def profile_view(request):
    # profile, _ = Profile.objects.get_or_create(user=request.user)
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = WarehouseProfileForm(
            request.POST, request.FILES, instance=profile
        )

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()

            messages.success(request, _("Profile successfully updated."))
            return redirect("accounts:profile")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = WarehouseProfileForm(instance=profile)

    context = {
        "u_form": u_form,
        "p_form": p_form,
        "profile": profile,
    }
    return render(request, "accounts/profile.html", context)


# Обновление базовых полей учетной записи (имя, фамилия, email)
class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ["first_name", "last_name", "email"]
    template_name = "accounts/my_account.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user


# ==========================================
# УПРАВЛЕНИЕ СКЛАДСКИМ ПЕРСОНАЛОМ (КЛАДОВЩИКИ)
# ==========================================

# Просмотр списка кладовщиков / операторов склада для менеджера и админа
class StorekeeperListView(ManagerRequiredMixin, ListView):
    model = Profile
    template_name = "accounts/storekeeper_list.html"
    context_object_name = "storekeepers"

    def get_queryset(self):
        return (
            Profile.objects.filter(role="storekeeper")
            .select_related("user")
            .order_by("user__last_name")
        )


# Добавление нового кладовщика в систему
class StorekeeperCreateView(ManagerRequiredMixin, CreateView):
    form_class = CustomUserCreationForm
    template_name = "accounts/storekeeper_form.html"
    success_url = reverse_lazy("accounts:storekeeper_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        profile, _ = Profile.objects.get_or_create(user=self.object)
        profile.role = "storekeeper"
        profile.save()
        messages.success(self.request, _("Storekeeper account successfully created."))
        return response


# Редактирование данных кладовщика (телефон, табельный номер / штрихкод)
class StorekeeperUpdateView(ManagerRequiredMixin, UpdateView):
    model = Profile
    fields = ["phone", "employee_code", "avatar"]
    template_name = "accounts/storekeeper_form.html"
    success_url = reverse_lazy("accounts:storekeeper_list")

    def get_queryset(self):
        return Profile.objects.filter(role="storekeeper")


# Удаление / деактивация кладовщика из системы
class StorekeeperDeleteView(ManagerRequiredMixin, DeleteView):
    model = User
    template_name = "accounts/storekeeper_confirm_delete.html"
    success_url = reverse_lazy("accounts:storekeeper_list")