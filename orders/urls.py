from django.urls import path
from orders import views
urlpatterns = [
    path('', views.menu_page, name="menu_page"),
    path('queue', views.queue_page, name="queue_page"),
    path('restaurant/orders', views.orders_page, name="orders_page"),
    path('restaurant/menus', views.restaurant_menu_page, name="restaurant_menu_page"),
    path('restaurant/orders/mark-as-done', views.mark_order_as_done, name="mark_order_as_done")
]