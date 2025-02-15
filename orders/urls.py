from django.urls import path
from orders import views
urlpatterns = [
    path('', views.menupage),
    path('queue', views.queuepage),
    path('restaurant/orders', views.orderspage)
]