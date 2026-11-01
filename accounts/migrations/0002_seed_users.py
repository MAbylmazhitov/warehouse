from django.db import migrations
from django.contrib.auth.hashers import make_password

def seed_users_and_groups(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Group = apps.get_model('auth', 'Group')
    Profile = apps.get_model('accounts', 'Profile')

    managers_group, _ = Group.objects.get_or_create(name='Managers')
    storekeepers_group, _ = Group.objects.get_or_create(name='Storekeepers')

    # Администратор
    admin_user, _ = User.objects.get_or_create(
        username='root',
        defaults={
            'email': 'admin@store.ru',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'password': make_password('SsNn5678+-@'),
            'is_staff': True,
            'is_superuser': True
        }
    )
    if admin_user.first_name != 'Иван' or admin_user.last_name != 'Иванов':
        admin_user.first_name = 'Иван'
        admin_user.last_name = 'Иванов'
        admin_user.save()

    Profile.objects.update_or_create(
        user=admin_user,
        defaults={'role': 'admin', 'phone': '+79990000000', 'employee_code': 'EMP-ADM-001'}
    )

    # Менеджер
    mgr, _ = User.objects.get_or_create(
        username='manager',
        defaults={
            'email': 'manager@store.ru',
            'first_name': 'Алексей',
            'last_name': 'Смирнов',
            'password': make_password('Ss0066+-'),
            'is_staff': True
        }
    )
    if mgr.first_name != 'Алексей' or mgr.last_name != 'Смирнов':
        mgr.first_name = 'Алексей'
        mgr.last_name = 'Смирнов'
        mgr.save()

    mgr.groups.add(managers_group)
    Profile.objects.update_or_create(
        user=mgr,
        defaults={'role': 'manager', 'phone': '+79999998877', 'employee_code': 'EMP-MGR-001'}
    )

    # Кладовщики (5 сотрудников)
    storekeepers_data = [
        ("storekeeper1", "Дмитрий", "Васильев", "+79991112233", "SK-1001"),
        ("storekeeper2", "Елена", "Петрова", "+79992223344", "SK-1002"),
        ("storekeeper3", "Михаил", "Соколов", "+79993334455", "SK-1003"),
        ("storekeeper4", "Ольга", "Михайлова", "+79994445566", "SK-1004"),
        ("storekeeper5", "Андрей", "Новиков", "+79995556677", "SK-1005"),
    ]
    for uname, fname, lname, phone, code in storekeepers_data:
        u, created = User.objects.get_or_create(
            username=uname,
            defaults={
                'email': f"{uname}@store.ru",
                'first_name': fname,
                'last_name': lname,
                'password': make_password('Password123!')
            }
        )
        if not created and (u.first_name != fname or u.last_name != lname):
            u.first_name = fname
            u.last_name = lname
            u.save()

        u.groups.add(storekeepers_group)
        Profile.objects.update_or_create(
            user=u,
            defaults={'role': 'storekeeper', 'phone': phone, 'employee_code': code}
        )

def reverse_seed_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Group = apps.get_model('auth', 'Group')
    User.objects.filter(username__in=['root', 'manager'] + [f"storekeeper{i}" for i in range(1, 6)]).delete()
    Group.objects.filter(name__in=['Managers', 'Storekeepers']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(seed_users_and_groups, reverse_code=reverse_seed_users),
    ]