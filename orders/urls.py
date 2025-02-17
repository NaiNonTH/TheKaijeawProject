from django.urls import path
from orders import views
urlpatterns = [
    path('', views.menupage, name="menu_page"),
    path('queue', views.queuepage, name="queue_page"),
    path('restaurant/orders', views.orderspage, name="orders_page"),
    path('restaurant/orders/mark-as-done', views.mark_order_as_done, name="mark_order_as_done")
]