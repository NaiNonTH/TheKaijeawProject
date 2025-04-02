from .models import Restaurant

from django.forms import models

class RestaurantForm(models.ModelForm):
    class Meta:
        def __init__(self):
            pass

        model = Restaurant
        fields = ["queue_capacity", "max_fillings"]
        labels = {
            "queue_capacity": "จำนวนคิวสูงสุด",
            "max_fillings": "จำนวนไส้สูงสุด"
        }