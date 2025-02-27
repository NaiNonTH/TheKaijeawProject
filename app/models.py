from django.db import models

# Create your models here.

class Filling(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    title = models.TextField(default="Untitled")
    is_available = models.BooleanField(default=True)

class Egg(models.Model):
    amount = models.PositiveSmallIntegerField(primary_key=True)
    price = models.PositiveSmallIntegerField()

class Order(models.Model):
    queue_number = models.PositiveSmallIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    is_takeaway = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    fillings = models.ManyToManyField(Filling, blank=True)
    egg_amount = models.ForeignKey(Egg, on_delete=models.DO_NOTHING)

    def mark_as_done(self):
        self.is_completed = True
        self.save()

class Restaurant(models.Model):
    queue_capacity = models.PositiveSmallIntegerField(default=20)
    max_fillings = models.PositiveSmallIntegerField(default=3)
    is_opened = models.BooleanField(default=False)
    allow_takeaway = models.BooleanField(default=True)