from django.db import models
from django.utils import timezone

# Create your models here.
''' ยังไม่เสร็จ
class order(models.Mdoel):
    queue_number = models.IntegerField()
    order_timer = models.DateField(auto_now_add=True)
    filling = models.TextField()
    egg_amount = models.IntegerField(default=1)
    is_takeaway = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    def mark_as_done(self):
        self.is_completed = True
        self.save()
        statistics.update_statistics(self)
    def calculate_price(self):
        base_price = 25
        extra_egg = 5 * (self.egg_amount - 1)
        return base_price + extra_egg 

class statistics(models.Model):
    date = models.DateField(default=timezone.now)
    revenue = models.IntegerField(default=0)
    filling_stat = models.JSONField(default=dict)
    egg_amount = models.IntegerField(default=0)
    order_count = models.IntegerField(default=0)
    def update_statistics(cls, order):
        stats, created = cls.objectes.get(date=timezone.now().date())
        stats.order_count += 1
        stats.egg_amount += order.egg_amount
        stats.revenue += 0
        for filling in order.fillings.all():
            if filling.name in stats.fillings_stat:
                stats.filling_stats

class filling(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_avaiable = models.BooleanField(default=True)

class notification:
    def display_error(message):
        print("No Queue left")
'''
