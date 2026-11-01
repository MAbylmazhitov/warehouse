from decimal import Decimal
from django.db import migrations

def seed_inventory_and_docs(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Category = apps.get_model('inventory', 'Category')
    Product = apps.get_model('inventory', 'Product')
    StorageLocation = apps.get_model('inventory', 'StorageLocation')
    StockBalance = apps.get_model('inventory', 'StockBalance') # <-- Добавили модель остатков
    Contractor = apps.get_model('orders', 'Contractor')
    StockDocument = apps.get_model('orders', 'StockDocument')
    DocumentItem = apps.get_model('orders', 'DocumentItem')
    InventoryAudit = apps.get_model('orders', 'InventoryAudit')

    admin_user = User.objects.filter(username='root').first()

    # 1. Категории
    categories_data = [
        ('Инструмент', 'Ручной и электроинструмент'),
        ('Силовое', 'Генераторы и сварочные аппараты'),
        ('Подъемное', 'Леса, вышки, домкраты'),
        ('Измерительное', 'Нивелиры, уровни, дальномеры'),
        ('Садовое и парковое', 'Мотобуры, газонокосилки, пилы'),
        ('Климатическое', 'Тепловые пушки, осушители'),
        ('Дорожно-строительное', 'Виброплиты, швонарезчики'),
        ('Сварочное', 'Инверторы, полуавтоматы'),
        ('Уборочное', 'Пылесосы, мойки высокого давления'),
        ('Пневматическое', 'Компрессоры, отбойные молотки'),
    ]
    created_categories = {}
    for idx, (name, desc) in enumerate(categories_data, 1):
        cat, _ = Category.objects.get_or_create(name=name, defaults={'description': desc, 'display_order': idx})
        created_categories[name] = cat

    # 2. Товары
    products_data = [
        ('INST-001', '4607001001', 'Перфоратор Bosch GBH 2-28', 'Инструмент', 'шт', 2),
        ('INST-002', '4607001002', 'Бур SDS-max 40x400 мм', 'Инструмент', 'шт', 5),
        ('INST-003', '4607001003', 'Угловая шлифмашина Makita GA9020', 'Инструмент', 'шт', 3),
        ('INST-004', '4607001004', 'Шуруповерт аккумуляторный DeWalt', 'Инструмент', 'шт', 4),
        ('PWR-001', '4607002001', 'Генератор 5 кВт бензиновый', 'Силовое', 'шт', 1),
        ('PWR-002', '4607002002', 'Инверторный генератор 2.5 кВт', 'Силовое', 'шт', 2),
        ('PWR-003', '4607002003', 'Стабилизатор напряжения 10 кВА', 'Силовое', 'шт', 1),
        ('LIFT-001', '4607003001', 'Вышка-тура строительная 6м', 'Подъемное', 'компл', 1),
        ('LIFT-002', '4607003002', 'Таль ручная цепная 1т', 'Подъемное', 'шт', 2),
        ('LIFT-003', '4607003003', 'Домкрат гидравлический 10т', 'Подъемное', 'шт', 3),
        ('MEAS-001', '4607004001', 'Нивелир оптический Leica', 'Измерительное', 'шт', 1),
        ('MEAS-002', '4607004002', 'Лазерный уровень 4D Bosch', 'Измерительное', 'шт', 2),
        ('MEAS-003', '4607004003', 'Дальномер лазерный 80м', 'Измерительное', 'шт', 3),
        ('GAR-001', '4607005001', 'Мотобур бензиновый со шнеком', 'Садовое и парковое', 'шт', 1),
        ('GAR-002', '4607005002', 'Бензопила Stihl MS 180', 'Садовое и парковое', 'шт', 2),
        ('GAR-003', '4607005003', 'Газонокосилка бензиновая', 'Садовое и парковое', 'шт', 1),
        ('CLIM-001', '4607006001', 'Тепловая пушка дизельная 30 кВт', 'Климатическое', 'шт', 2),
        ('CLIM-002', '4607006002', 'Осушитель воздуха промышленный', 'Климатическое', 'шт', 2),
        ('CLIM-003', '4607006003', 'Вентилятор мобильный промышленный', 'Климатическое', 'шт', 3),
        ('ROAD-001', '4607007001', 'Виброплита бензиновая 90 кг', 'Дорожно-строительное', 'шт', 2),
        ('ROAD-002', '4607007002', 'Швонарезчик бензиновый', 'Дорожно-строительное', 'шт', 1),
        ('ROAD-003', '4607007003', 'Трамбовка вибрационная', 'Дорожно-строительное', 'шт', 1),
        ('WELD-001', '4607008001', 'Сварочный инвертор Ресанта САИ-220', 'Сварочное', 'шт', 3),
        ('WELD-002', '4607008002', 'Полуавтомат сварочный MIG/MAG', 'Сварочное', 'шт', 2),
        ('WELD-003', '4607008003', 'Аппарат аргонодуговой сварки TIG', 'Сварочное', 'шт', 1),
        ('CLEAN-001', '4607009001', 'Строительный пылесос Karcher NT 30/1', 'Уборочное', 'шт', 2),
        ('CLEAN-002', '4607009002', 'Мойка высокого давления Karcher HD', 'Уборочное', 'шт', 2),
        ('CLEAN-003', '4607009003', 'Пароочиститель профессиональный', 'Уборочное', 'шт', 1),
        ('CLEAN-004', '4607009004', 'Поломоечная машина аккумуляторная', 'Уборочное', 'шт', 1),
        ('PNEM-001', '4607010001', 'Компрессор поршневой 100 л', 'Пневматическое', 'шт', 2),
        ('PNEM-002', '4607010002', 'Пневмомолоток отбойный', 'Пневматическое', 'шт', 3),
        ('PNEM-003', '4607010003', 'Набор пневмоинструмента ударный', 'Пневматическое', 'шт', 3),
        ('PNEM-004', '4607010004', 'Краскопульт пневматический', 'Пневматическое', 'шт', 4),
    ]
    created_products = {}
    for sku, barcode_val, title, cat_name, unit_val, min_val in products_data:
        prod, _ = Product.objects.get_or_create(
            sku=sku,
            defaults={
                'barcode': barcode_val,
                'name': title,
                'category': created_categories[cat_name],
                'unit': unit_val,
                'min_stock': min_val,
                'is_active': True
            }
        )
        created_products[sku] = prod

    # 3. Места хранения
    locations = []
    for zone_val in ['A', 'B', 'C', 'D']:
        for rack_val in range(1, 3):
            for shelf_val in range(1, 3):
                for cell_val in range(1, 3):
                    loc_code = f"{zone_val}-{rack_val:02d}-{shelf_val:02d}-{cell_val:02d}"
                    loc, _ = StorageLocation.objects.get_or_create(
                        zone=zone_val,
                        rack=f"R-{rack_val:02d}",
                        shelf=f"S-{shelf_val:02d}",
                        cell=f"C-{cell_val:02d}",
                        defaults={'barcode': f"BAR-{loc_code}"}
                    )
                    locations.append(loc)
                    if len(locations) >= 20:
                        break
                if len(locations) >= 20:
                    break
            if len(locations) >= 20:
                break
        if len(locations) >= 20:
            break

    # 4. Контрагенты
    contractors_data = [
        ('ООО «СтройМонтажСервис»', 'customer', '7704123456', '+77011111111'),
        ('ИП Иванов Алексей Петрович', 'customer', '4505123456', '+77022222222'),
        ('ООО «РегионСтройГрупп»', 'customer', '5032987654', '+77033333333'),
        ('Смирнов Дмитрий Сергеевич', 'customer', '4602987123', '+77044444444'),
        ('АО «Монолит-Фундамент»', 'customer', '7728111222', '+77055555555'),
        ('ИП Кузнецова Елена Викторовна', 'customer', '4510555444', '+77066666666'),
        ('ООО «Альянс-Инжиниринг»', 'customer', '7715678901', '+77077777777'),
        ('Васильев Николай Павлович', 'customer', '4501333222', '+77088888888'),
        ('ООО «СпецТрансСтрой»', 'customer', '7721543210', '+77099999999'),
        ('Петров Сергей Владимирович', 'customer', '4508778899', '+77010101010'),
        ('ТОО «КазСтройПром»', 'supplier', '120340001234', '+77020202020'),
        ('ТОО «Инструмент-Сервис»', 'supplier', '150440005678', '+77030303030'),
        ('ООО «МеталлТрейд»', 'supplier', '7701234567', '+77040404040'),
        ('АО «ЭлектроТехника»', 'supplier', '7702345678', '+77050505050'),
        ('ТОО «СтройРесурс KZ»', 'supplier', '180640009876', '+77060606060'),
        ('ИП Султанов Б.К.', 'supplier', '790512345678', '+77070707070'),
        ('ТОО «ПромОборудование»', 'supplier', '140140004321', '+77080808080'),
        ('ООО «ТехноСнаб»', 'supplier', '7709876543', '+77090909090'),
        ('ТОО «Альфа-Логистик»', 'supplier', '160240001122', '+77012121212'),
        ('ИП Омаров Д.Ж.', 'supplier', '820412345678', '+77013131313'),
    ]
    created_contractors = {}
    for name, c_type, tax_id, phone in contractors_data:
        c, _ = Contractor.objects.get_or_create(
            name=name,
            defaults={'contractor_type': c_type, 'tax_id': tax_id, 'phone': phone}
        )
        created_contractors[name] = c

    # 5. Складские документы
    doc_types = ['incoming', 'outgoing', 'transfer', 'audit']
    prod_keys = list(created_products.keys())
    contractor_keys = list(created_contractors.keys())

    for i in range(1, 21):
        doc_num = f"DOC-{i:03d}"
        if StockDocument.objects.filter(doc_number=doc_num).exists():
            continue

        d_type = doc_types[(i - 1) % len(doc_types)]
        contractor_name = contractor_keys[(i - 1) % len(contractor_keys)]

        doc = StockDocument.objects.create(
            doc_number=doc_num,
            doc_type=d_type,
            contractor=created_contractors[contractor_name],
            author=admin_user,
            status='conducted',
            comment=f"Автоматически сгенерированный документ №{i}"
        )

        p1 = created_products[prod_keys[(i - 1) % len(prod_keys)]]
        p2 = created_products[prod_keys[i % len(prod_keys)]]
        loc_src = locations[i % len(locations)]
        loc_tgt = locations[(i + 1) % len(locations)]

        DocumentItem.objects.create(
            document=doc,
            product=p1,
            source_location=loc_src,
            target_location=loc_tgt,
            quantity=Decimal('5.000'),
            price=Decimal('1500.00')
        )
        DocumentItem.objects.create(
            document=doc,
            product=p2,
            source_location=loc_tgt,
            target_location=loc_src,
            quantity=Decimal('2.000'),
            price=Decimal('3000.00')
        )

        if d_type == 'audit':
            InventoryAudit.objects.create(
                document=doc,
                product=p1,
                location=loc_src,
                accounting_quantity=Decimal('5.000'),
                actual_quantity=Decimal('4.000'),
                difference=Decimal('-1.000')
            )

    # 6. НАПОЛНЕНИЕ ТАБЛИЦЫ ОСТАТКОВ (StockBalance) ДЛЯ ОТОБРАЖЕНИЯ НА СТРАНИЦЕ
    for idx, (sku, prod) in enumerate(created_products.items()):
        loc = locations[idx % len(locations)]
        # Присваиваем каждому товару остаток (например, 15 штук), чтобы quantity > 0
        StockBalance.objects.get_or_create(
            product=prod,
            location=loc,
            defaults={'quantity': Decimal('15.000')}
        )

def reverse_seed_inventory(apps, schema_editor):
    Category = apps.get_model('inventory', 'Category')
    Contractor = apps.get_model('orders', 'Contractor')
    StockDocument = apps.get_model('orders', 'StockDocument')
    StockBalance = apps.get_model('inventory', 'StockBalance')

    StockBalance.objects.all().delete()
    StockDocument.objects.all().delete()
    Contractor.objects.all().delete()
    Category.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0002_seed_users'),
        ('inventory', '0001_initial'),
        ('orders', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(seed_inventory_and_docs, reverse_code=reverse_seed_inventory),
    ]