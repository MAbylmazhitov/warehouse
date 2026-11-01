from decimal import Decimal
from django.db import migrations


def create_orders_data(apps, schema_editor):
    Contractor = apps.get_model('orders', 'Contractor')
    StockDocument = apps.get_model('orders', 'StockDocument')
    DocumentItem = apps.get_model('orders', 'DocumentItem')
    User = apps.get_model('auth', 'User')

    Product = apps.get_model('inventory', 'Product')
    StorageLocation = apps.get_model('inventory', 'StorageLocation')

    # Получаем первого пользователя в системе в качестве автора документов (или создаем системного)
    author = User.objects.first()

    # 1. Справочник контрагентов
    contractors_data = [
        {
            'name': 'ООО «ТехноПромПоставка»',
            'contractor_type': 'supplier',
            'tax_id': '7701234567',
            'phone': '+7 (495) 100-20-30',
            'email': 'supply@technoprom.ru',
            'address': 'г. Москва, ул. Складская, д. 15, стр. 2',
        },
        {
            'name': 'АО «ЛогистикРесурс»',
            'contractor_type': 'supplier',
            'tax_id': '7809876543',
            'phone': '+7 (812) 400-50-60',
            'email': 'info@logresource.spb.ru',
            'address': 'г. Санкт-Петербург, Московское шоссе, д. 42',
        },
        {
            'name': 'ИП Сидоров А. В. (Сеть магазинов)',
            'contractor_type': 'customer',
            'tax_id': '502401122334',
            'phone': '+7 (916) 555-44-33',
            'email': 'sidorov_shop@mail.ru',
            'address': 'г. Химки, ул. Маяковского, д. 8',
        },
    ]

    created_contractors = {}
    for c_data in contractors_data:
        contractor, _ = Contractor.objects.get_or_create(
            name=c_data['name'],
            defaults=c_data
        )
        created_contractors[c_data['name']] = contractor

    # Достаем товары и ячейки, созданные в миграциях inventory
    switch_prod = Product.objects.filter(sku='SKU-EL-001').first()
    cable_prod = Product.objects.filter(sku='SKU-EL-002').first()
    stretch_prod = Product.objects.filter(sku='SKU-EQ-001').first()

    loc_a1 = StorageLocation.objects.filter(zone='A', rack='01', shelf='1', cell='01').first()
    loc_a2 = StorageLocation.objects.filter(zone='A', rack='01', shelf='1', cell='02').first()
    loc_b1 = StorageLocation.objects.filter(zone='B', rack='01', shelf='1', cell='01').first()

    if not author or not switch_prod or not loc_a1:
        return

    # 2. Создание документов и табличной части
    # Документ 1: Приходная накладная (Проведен)
    doc_inc, _ = StockDocument.objects.get_or_create(
        doc_number='REC-2026-0001',
        defaults={
            'doc_type': 'incoming',
            'status': 'conducted',
            'contractor': created_contractors.get('ООО «ТехноПромПоставка»'),
            'author': author,
            'comment': 'Первичный приход сетевого оборудования от поставщика',
        }
    )
    
    DocumentItem.objects.get_or_create(
        document=doc_inc,
        product=switch_prod,
        defaults={
            'target_location': loc_a1,
            'quantity': Decimal('12.000'),
            'price': Decimal('28500.00'),
        }
    )

    if cable_prod and loc_a2:
        DocumentItem.objects.get_or_create(
            document=doc_inc,
            product=cable_prod,
            defaults={
                'target_location': loc_a2,
                'quantity': Decimal('45.000'),
                'price': Decimal('4200.00'),
            }
        )

    # Документ 2: Расходная накладная (Черновик)
    doc_out, _ = StockDocument.objects.get_or_create(
        doc_number='EXP-2026-0001',
        defaults={
            'doc_type': 'outgoing',
            'status': 'draft',
            'contractor': created_contractors.get('ИП Сидоров А. В. (Сеть магазинов)'),
            'author': author,
            'comment': 'Отгрузка по заявке №402',
        }
    )

    if stretch_prod and loc_b1:
        DocumentItem.objects.get_or_create(
            document=doc_out,
            product=stretch_prod,
            defaults={
                'source_location': loc_b1,
                'quantity': Decimal('10.000'),
                'price': Decimal('650.00'),
            }
        )


def reverse_orders_data(apps, schema_editor):
    Contractor = apps.get_model('orders', 'Contractor')
    StockDocument = apps.get_model('orders', 'StockDocument')

    StockDocument.objects.all().delete()
    Contractor.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
        ('inventory', '0002_seed_inventory'),  # Указываем зависимость от дата-миграции inventory
    ]

    operations = [
        migrations.RunPython(create_orders_data, reverse_code=reverse_orders_data),
    ]