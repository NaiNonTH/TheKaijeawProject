from django.contrib import admin
from .models import Filling, Order, Egg, Restaurant
from django import forms

# Register your models here.

admin.site.register(Filling)
admin.site.register(Order)
admin.site.register(Egg)

class RestaurantAdminForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = '__all__'

class RestaurantAdmin(admin.ModelAdmin):
    form = RestaurantAdminForm
    list_display = ('queue_capacity', 'is_opened', 'allow_takeaway')

admin.site.register(Restaurant, RestaurantAdmin)