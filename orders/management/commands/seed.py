"""
Comando: python manage.py seed
-------------------------------
Pobla la base de datos con datos de prueba:
  - 1 superusuario (admin / admin123)
  - 3 restaurantes
  - 4 categorías
  - 12 productos

Uso:
  python manage.py seed              # crea datos si no existen
  python manage.py seed --flush      # borra todo y recrea desde cero
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from orders.models import Restaurant, Category, Product


RESTAURANTS = [
    {
        'name':    'La Parrilla del Chef',
        'address': 'Calle 10 # 43-20, El Poblado',
        'phone':   '604-555-0101',
        'rating':  4.8,
    },
    {
        'name':    'Sushi Nakamura',
        'address': 'Carrera 37 # 8A-15, Laureles',
        'phone':   '604-555-0202',
        'rating':  4.6,
    },
    {
        'name':    'Pizza Nápoli Express',
        'address': 'Av. El Retiro # 3-44, Envigado',
        'phone':   '604-555-0303',
        'rating':  4.3,
    },
]

CATEGORIES = ['Hamburguesas', 'Sushi', 'Pizzas', 'Bebidas']

PRODUCTS = [
    # Hamburguesas — La Parrilla del Chef
    {
        'name':        'Burger Clásica',
        'description': 'Carne angus 200g, lechuga, tomate, cebolla caramelizada',
        'price':       18900,
        'stock':       30,
        'category':    'Hamburguesas',
        'restaurant':  'La Parrilla del Chef',
    },
    {
        'name':        'Burger BBQ Doble',
        'description': 'Doble carne, bacon crocante, salsa BBQ ahumada',
        'price':       24900,
        'stock':       25,
        'category':    'Hamburguesas',
        'restaurant':  'La Parrilla del Chef',
    },
    {
        'name':        'Burger Veggie',
        'description': 'Medallón de lentejas, aguacate, pico de gallo',
        'price':       16900,
        'stock':       20,
        'category':    'Hamburguesas',
        'restaurant':  'La Parrilla del Chef',
    },
    # Sushi — Sushi Nakamura
    {
        'name':        'Roll California',
        'description': '8 piezas — cangrejo, aguacate, pepino, sésamo',
        'price':       22000,
        'stock':       15,
        'category':    'Sushi',
        'restaurant':  'Sushi Nakamura',
    },
    {
        'name':        'Roll Spicy Tuna',
        'description': '8 piezas — atún, mayo picante, cebollín',
        'price':       26000,
        'stock':       12,
        'category':    'Sushi',
        'restaurant':  'Sushi Nakamura',
    },
    {
        'name':        'Sashimi Salmón x6',
        'description': '6 láminas de salmón fresco con wasabi y jengibre',
        'price':       31000,
        'stock':       10,
        'category':    'Sushi',
        'restaurant':  'Sushi Nakamura',
    },
    # Pizzas — Pizza Nápoli Express
    {
        'name':        'Pizza Margherita',
        'description': 'Salsa de tomate San Marzano, mozzarella fresca, albahaca',
        'price':       28000,
        'stock':       20,
        'category':    'Pizzas',
        'restaurant':  'Pizza Nápoli Express',
    },
    {
        'name':        'Pizza Pepperoni',
        'description': 'Doble pepperoni, mozzarella, orégano',
        'price':       32000,
        'stock':       18,
        'category':    'Pizzas',
        'restaurant':  'Pizza Nápoli Express',
    },
    {
        'name':        'Pizza 4 Quesos',
        'description': 'Mozzarella, gouda, parmesano, queso azul',
        'price':       34000,
        'stock':       15,
        'category':    'Pizzas',
        'restaurant':  'Pizza Nápoli Express',
    },
    # Bebidas — todos los restaurantes
    {
        'name':        'Limonada de Coco',
        'description': 'Limonada natural con leche de coco, 500ml',
        'price':       8000,
        'stock':       50,
        'category':    'Bebidas',
        'restaurant':  'La Parrilla del Chef',
    },
    {
        'name':        'Té Matcha Frío',
        'description': 'Matcha japonés con leche de almendras, 400ml',
        'price':       9500,
        'stock':       40,
        'category':    'Bebidas',
        'restaurant':  'Sushi Nakamura',
    },
    {
        'name':        'Agua Panela con Limón',
        'description': 'Tradicional bebida colombiana, 300ml',
        'price':       5000,
        'stock':       60,
        'category':    'Bebidas',
        'restaurant':  'Pizza Nápoli Express',
    },
]


class Command(BaseCommand):
    help = 'Pobla la BD con restaurantes, categorías y productos de prueba'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Borra todos los datos existentes antes de insertar',
        )

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write('🗑  Borrando datos existentes...')
            Product.objects.all().delete()
            Category.objects.all().delete()
            Restaurant.objects.all().delete()
            User.objects.filter(is_superuser=True).delete()
            self.stdout.write(self.style.WARNING('   Datos borrados.'))

        # ── Superusuario ───────────────────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@quickbite.com',
                password='admin123',
            )
            self.stdout.write(self.style.SUCCESS('✅ Superusuario creado → admin / admin123'))
        else:
            self.stdout.write('   Superusuario admin ya existe — omitido.')

        # ── Restaurantes ───────────────────────────────────────────────────
        restaurants = {}
        for r in RESTAURANTS:
            obj, created = Restaurant.objects.get_or_create(
                name=r['name'],
                defaults={
                    'address': r['address'],
                    'phone':   r['phone'],
                    'rating':  r['rating'],
                }
            )
            restaurants[r['name']] = obj
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Restaurante: {obj.name}'))

        # ── Categorías ─────────────────────────────────────────────────────
        categories = {}
        for name in CATEGORIES:
            obj, created = Category.objects.get_or_create(name=name)
            categories[name] = obj
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Categoría: {obj.name}'))

        # ── Productos ──────────────────────────────────────────────────────
        created_count = 0
        for p in PRODUCTS:
            obj, created = Product.objects.get_or_create(
                name=p['name'],
                defaults={
                    'description': p['description'],
                    'price':       p['price'],
                    'stock':       p['stock'],
                    'category':    categories[p['category']],
                    'restaurant':  restaurants[p['restaurant']],
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'✅ {created_count} productos creados'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🚀 Seed completado!'))
        self.stdout.write('   Frontend:  http://localhost')
        self.stdout.write('   Admin:     http://localhost/admin')
        self.stdout.write('   Usuario:   admin')
        self.stdout.write('   Contraseña: admin123')
