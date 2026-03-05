from django.contrib import admin
<<<<<<< HEAD

# Register your models here.
=======
from .models import Product, Order, OrderItem, Payment

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
>>>>>>> 571b5ab (Implementación de modelos, builder, servicios y factory)
