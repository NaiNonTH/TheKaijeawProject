from django.shortcuts import render
from django.http import HttpRequest, HttpResponseRedirect

from .models import Filling, Egg, Order, Restaurant, Validator
from .utils import OrderBuilder

# Create your views here.

def menu_page(request: HttpRequest):
    restaurant = Restaurant.objects.last()

    if not restaurant.is_opened:
        return render(request, "customer/closed.html")

    fillings = Filling.objects.all()
    eggs = Egg.objects.all()

    context = {
        "fillings": fillings,
        "eggs": eggs,
        "restaurant": restaurant
    }

    return render(request, "customer/menupage.html", context)

def queue_page(request: HttpRequest):
    if request and request.method == "POST":
        try:
            if "egg" not in request.POST:
                raise Validator.NoEggAmountSpecifiedError

            egg_amount = request.POST["egg"]
            fillings_list = request.POST.getlist("filling")
            is_takeaway = "is_takeaway" in request.POST

            new_order = OrderBuilder(egg_amount)        \
                        .add_fillings(fillings_list)    \
                        .takeaway(is_takeaway)          \
                        .build()                        \

        except Validator.NoQueueLeftError:
            context = {
                "is_error": False,
                "status_code": 400,
                "message": "ไม่มีคิวว่าง"
            }

            return render(request, "customer/error.html", context, status=400)
        except Validator.NoEggAmountSpecifiedError:
            context = {
                "is_error": False,
                "status_code": 400,
                "message": "ท่านไม่ได้ระบุจำนวนไข่"
            }
            
            return render(request, "customer/error.html", context, status=400)
        except Validator.TooManyFillingsError:
            context = {
                "is_error": False,
                "status_code": 400,
                "message": "ท่านเลือกไส้เกิน 3 ตัวเลือก"
            }

            return render(request, "customer/error.html", context, status=400)
        except Exception:
            context = {
                "is_error": True,
                "status_code": 500,
                "message": "เกิดข้อผิดพลาดโดยไม่ทราบสาเหตุในระบบ"
            }

            return render(request, "customer/error.html", context, status=500)
        
        context = {
            "queue_number": new_order.queue_number,
            "price": new_order.egg_amount.price
        }

        return render(request, "customer/queuepage.html", context)
    else:
        context = {
            "is_error": False,
            "status_code": 405,
            "message": "ท่านไม่ได้เข้ามาหน้านี้อย่างถูกต้อง"
        }

        return render(request, "customer/error.html", context, status=405)
    
def restaurant_menu_page(request: HttpRequest):
    fillings = list(Filling.objects.all())
    restaurant = Restaurant.objects.last()

    print(restaurant)

    context = {
        "fillings": fillings,
        "restaurant": restaurant
    }

    return render(request, "restaurant/menupage.html", context)
    
def orders_page(request: HttpRequest):
    orders = list(Order.objects.filter(is_completed=False).all())

    context = {
        "orders": orders
    }

    return render(request, "restaurant/orderspage.html", context)

def mark_order_as_done(request: HttpRequest):
    if request.method == "POST":
        try:
            if "id" not in request.POST:
                raise Order.DoesNotExist

            Order.objects.get(pk=request.POST['id']).mark_as_done()

            return HttpResponseRedirect("/restaurant/orders")
        except (Order.DoesNotExist):
            context = {
                "is_error": True,
                "status_code": 400,
                "message": "ไม่พบคำสั่งซื้อดังกล่าว",
                "previous_page": "/restaurant/orders" 
            }

            return render(request, "restaurant/error.html", context, status=400)
        except Exception:
            context = {
                "is_error": True,
                "status_code": 500,
                "message": "เกิดข้อผิดพลาดโดยไม่ทราบสาเหตุในระบบ"
            }

            return render(request, "restaurant/error.html", context, status=500)
    else:
        context = {
            "is_error": False,
            "status_code": 405,
            "message": "ท่านไม่ได้เข้ามาหน้านี้อย่างถูกต้อง",
        }

        return render(request, "restaurant/error.html", context, status=405)

def update_filling_availability(request: HttpRequest):
    if request.method == "POST":
        req_fillings =  request.POST.getlist("filling")

        Filling.objects                     \
            .filter(name__in=req_fillings)  \
            .update(is_available=True)
        
        Filling.objects                     \
            .exclude(name__in=req_fillings) \
            .update(is_available=False)
        
        return HttpResponseRedirect("/restaurant/menus")
    else:
        context = {
            "is_error": False,
            "status_code": 405,
            "message": "ท่านไม่ได้เข้ามาหน้านี้อย่างถูกต้อง",
        }
        
        return render(request, "restaurant/error.html", context, status=405)
    
def toggle_takeaway(request: HttpRequest):
    if request.method == "POST":
        req_allow_takeaway = "box" in request.POST

        Restaurant.objects.update(allow_takeaway=req_allow_takeaway)
        
        return HttpResponseRedirect("/restaurant/menus")
    else:
        context = {
            "is_error": False,
            "status_code": 405,
            "message": "ท่านไม่ได้เข้ามาหน้านี้อย่างถูกต้อง",
        }
        
        return render(request, "restaurant/error.html", context, status=405)
    
def toggle_restaurant(request: HttpRequest):
    if request.method == "POST":
        req_is_opened = "is_opened" in request.POST

        Restaurant.objects.update(is_opened=req_is_opened)
        
        return HttpResponseRedirect("/restaurant/menus")
    else:
        context = {
            "is_error": False,
            "status_code": 405,
            "message": "ท่านไม่ได้เข้ามาหน้านี้อย่างถูกต้อง",
        }
        
        return render(request, "restaurant/error.html", context, status=405)