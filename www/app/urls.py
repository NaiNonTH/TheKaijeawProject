from django.urls import path
from app import views

urlpatterns = [
    path('', views.menu_page, name="menu_page"),
    path('save-order', views.save_order, name="save_order"),
    path('queue', views.queue_page, name="queue_page"),
    path('restaurant/', views.restaurant_section),
    path('restaurant/login/authenticate', views.restaurant_authentication, name="authenticate"),
    path('restaurant/login/', views.login_view, name='login'),
    path('restaurant/logout/', views.logout_view, name='logout'),
    path('restaurant/orders', views.orders_page, name="orders_page"),
    path('restaurant/orders/mark-as-done', views.mark_order_as_done, name="mark_order_as_done"),
    path('restaurant/menus', views.restaurant_menu_page, name="restaurant_menu_page"),
    path('restaurant/menus/update-status', views.update_status, name="update_status"),
    path('restaurant/statistics', views.statistics_page, name="statistics_page"),
    path('restaurant/more', views.more_page, name="more_page"),
    path('restaurant/restaurant', views.restaurant_config, name="restaurant_config"),
    path('restaurant/change-restaurant-info', views.change_restaurant_info, name="change_restaurant_info"),
    path('restaurant/password', views.password_config, name="password_config"),
    path('restaurant/change-password', views.password_change, name="password_change"),
]