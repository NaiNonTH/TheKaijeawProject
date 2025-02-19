from django.shortcuts import render
from django.http import HttpRequest, HttpResponseRedirect

from .models import Filling, Egg, Order, Restaurant, Validator

# Create your views here.

def menu_page(request: HttpRequest):
    fillings = Filling.objects.all()
    eggs = Egg.objects.all()

    context = {
        "fillings": fillings,
        "eggs": eggs
    }

    return render(request, "customer/menupage.html", context)

def queue_page(request: HttpRequest):
    if request and request.method == "POST":
        try:
            if "egg" not in request.POST:
                raise Validator.NoEggAmountSpecifiedError

            fillings_list = request.POST.getlist("filling")
            is_takeaway = "is_takeaway" in request.POST

            if len(fillings_list) > 3:
                raise Validator.TooManyFillingsError

            egg_amount = Egg.objects.get(pk=request.POST['egg'])

            if len(Order.objects.filter(is_completed=False).all()) == 0:
                queue_number = 1
            else:
                incompleted_orders = Order.objects.filter(is_completed=False)
                unavailable_queues = [order.queue_number for order in list(incompleted_orders.all())]

                max_queue_number = 24

                if len(unavailable_queues) == max_queue_number:
                    raise Validator.NoQueueLeftError

                queue_number = unavailable_queues[-1] % max_queue_number + 1

                while queue_number in unavailable_queues:
                    queue_number = (queue_number + 1) % max_queue_number

            new_order = Order.objects.create(
                queue_number=queue_number,
                egg_amount=egg_amount,
                is_takeaway=is_takeaway
            )
            new_order.save()

            for filling_name in fillings_list:
                filling = Filling.objects.get(pk=filling_name)
                new_order.fillings.add(filling)

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
            "queue_number": queue_number,
            "price": egg_amount.price
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