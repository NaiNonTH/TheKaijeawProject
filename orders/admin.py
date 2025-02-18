from django.contrib import admin
from .models import Filling, Order, Egg, Restaurant
from django.contrib.auth.hashers import make_password
from django import forms

# Register your models here.

admin.site.register(Filling)
admin.site.register(Order)
admin.site.register(Egg)

class RestaurantAdminForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = '__all__'

    def clean_passcode(self):
        raw_passcode = self.cleaned_data.get('passcode')
        if raw_passcode:
            return make_password(raw_passcode)
        return raw_passcode

class RestaurantAdmin(admin.ModelAdmin):
    form = RestaurantAdminForm
    list_display = ('queue_capacity', 'is_opened', 'allow_takeaway')

admin.site.register(Restaurant, RestaurantAdmin)