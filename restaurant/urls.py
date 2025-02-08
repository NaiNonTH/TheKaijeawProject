from django.urls import path
from restaurant import views
urlpatterns = [
    path('login/', views.loginpage),
    path('order/', views.orderpage),
    path('summary/', views.summarypage),
    path('fillings/', views.fillingtogglepage)
]