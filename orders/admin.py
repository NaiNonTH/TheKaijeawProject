from django.contrib import admin
from .models import Filling, Order, Egg

# Register your models here.

admin.site.register(Filling)
admin.site.register(Order)
admin.site.register(Egg)