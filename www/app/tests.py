from django.test import TestCase, Client
from django.urls import reverse
from .models import Filling, Egg, Order, Restaurant
from .utils import OrderBuilder
# Create your tests here.

class ModelTests(TestCase):
    def setUp(self):
        self.filling_pork = Filling.objects.create(
            name="pork", 
            title="หมูสับ", 
            is_available=True
        )
        self.egg_two = Egg.objects.create(
            amount=2, 
            price=30
        )
        self.restaurant = Restaurant.objects.create(
            queue_capacity=5, 
            max_fillings=3, 
            is_opened=True, 
            allow_takeaway=True
        )

    def test_order_mark_as_done(self):
        order = Order.objects.create(
            queue_number=1,
            egg_amount=self.egg_two
        )
        self.assertFalse(order.is_completed, "Order should incomplete.")
        order.mark_as_done()
        self.assertTrue(order.is_completed, "Order should mark_as_done().")

    def test_restaurant_defaults(self):
        self.assertTrue(self.restaurant.is_opened)
        self.assertTrue(self.restaurant.allow_takeaway)
        self.assertEqual(self.restaurant.queue_capacity, 5)
        self.assertEqual(self.restaurant.max_fillings, 3)

#class UtilsTests(TestCase):

#class ViewTests(TestCase):
