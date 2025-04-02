from django.db import models
from django.core.validators import RegexValidator

# Create your models here.

filling_name_validator = RegexValidator(r"^[a-zA-z_]+$", "Only a-z, A-Z and Underscore ( _ ) characters are allowed")

class Filling(models.Model):
    name = models.CharField(max_length=100, primary_key=True, validators=[filling_name_validator])
    title = models.TextField(default="Untitled")
    is_available = models.BooleanField(default=True)

    def add(self, name, title):
        new_filling = self.objects.create(name=name, title=title, is_available=True)
        new_filling.save()

    def modify(self, name, title):
        self.objects.filter(name=name).update(name=name, title=title)

    def delete(self, name):
        self.objects.filter(name=name).delete()

class Egg(models.Model):
    amount = models.PositiveSmallIntegerField(primary_key=True)
    price = models.PositiveSmallIntegerField()

class Order(models.Model):
    queue_number = models.PositiveSmallIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    is_takeaway = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    fillings = models.ManyToManyField(Filling, blank=True)
    egg_amount = models.ForeignKey(Egg, on_delete=models.CASCADE)

    def mark_as_done(self):
        self.is_completed = True
        self.save()

class Restaurant(models.Model):
    queue_capacity = models.PositiveSmallIntegerField(default=20)
    max_fillings = models.PositiveSmallIntegerField(default=3)
    is_opened = models.BooleanField(default=False)
    allow_takeaway = models.BooleanField(default=True)