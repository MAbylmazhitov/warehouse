# Модели отображают информацию о данных, с которыми производится работа.
# Они содержат поля и поведение данных.
# Обычно одна модель представляет одну таблицу в базе данных.
# Каждая модель это класс унаследованный от django.db.models.Model.
# Атрибут модели представляет поле в базе данных.
# Django предоставляет автоматически созданное API для доступа к данным
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    Расширяет стандартную модель User ролями складского персонала (кладовщик, менеджер, администратор),
    контактными данными и табельным номером (штрихкодом бейджа).
    """
    ROLE_CHOICES = [
        ("storekeeper", _("Storekeeper / Warehouse Operator")),
        ("manager", _("Supply & Sales Manager")),
        ("admin", _("Warehouse Administrator")),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name=_("User"))
    role = models.CharField(_("Role"), max_length=20, choices=ROLE_CHOICES, default="storekeeper")
    phone = models.CharField(_("Phone Number"), max_length=20, blank=True, null=True)
    employee_code = models.CharField(_("Employee Badge / Barcode"), max_length=50, blank=True, null=True, unique=True, help_text=_("Barcode or badge code for quick TSD authorization"))
    avatar = models.ImageField(_("Avatar"), upload_to="avatars/", blank=True, null=True)

    class Meta:
        verbose_name = _("Warehouse Profile")
        verbose_name_plural = _("Warehouse Profiles")

    def __str__(self):
        full_name = self.user.get_full_name() or self.user.username
        return f"{full_name} — {self.get_role_display()}"

# ==========================================
# СИГНАЛЫ ДЛЯ АВТОМАТИЧЕСКОГО СОЗДАНИЯ ПРОФИЛЯ
# ==========================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Автоматически создает Profile при создании нового User."""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Гарантирует сохранение Profile при обновлении объекта User."""
    Profile.objects.get_or_create(user=instance)