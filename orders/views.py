from django.shortcuts import render
from django.http import HttpRequest, HttpResponseRedirect

from django.views.decorators.http import require_GET, require_POST

from .models import Filling, Egg, Order, Restaurant, Validator
from .utils import OrderBuilder

# Create your views here.

@require_GET
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

    if "success" in request.session and not request.session['success']:
        context["errors"] = request.session['error_message']

        request.session.flush()

    return render(request, "customer/menupage.html", context)

@require_POST
def save_order(request: HttpRequest):
    user_errors = []

    if "egg" not in request.POST:
        user_errors.append("ท่านไม่ได้ระบุจำนวนไข่")

    fillings_list = request.POST.getlist("filling")

    if len(fillings_list) > 3:
        user_errors.append("ท่านเลือกไส้เกิน 3 ตัวเลือก")

    if len(user_errors) > 0:
        request.session['success'] = False
        request.session['error_message'] = user_errors

        return HttpResponseRedirect("/")

    egg_amount = request.POST["egg"]
    is_takeaway = "is_takeaway" in request.POST

    try:
        new_order = OrderBuilder(egg_amount)        \
                    .add_fillings(fillings_list)    \
                    .takeaway(is_takeaway)          \
                    .build()
        
        new_order.save()

        request.session['success'] = True
        request.session['queue_number'] = new_order.queue_number
        request.session['price'] = new_order.egg_amount.price

    except Validator.NoQueueLeftError:
        request.session['success'] = False
        request.session['error_message'] = "ไม่มีคิวว่าง"
    
    return HttpResponseRedirect("queue")

@require_GET
def queue_page(request: HttpRequest):
    if "success" not in request.session:
        return HttpResponseRedirect("/")
    
    if request.session['success']:
        context = {
            "queue_number": request.session['queue_number'],
            "price": request.session['price']
        }

        return render(request, "customer/queuepage.html", context)
    else:
        context = {
            "message": request.session['error_message']
        }

        request.session.flush()

        return render(request, "customer/error.html", context)
    
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

@require_POST
def mark_order_as_done(request: HttpRequest):
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

@require_POST
def update_filling_availability(request: HttpRequest):
    req_fillings =  request.POST.getlist("filling")

    Filling.objects                     \
        .filter(name__in=req_fillings)  \
        .update(is_available=True)
    
    Filling.objects                     \
        .exclude(name__in=req_fillings) \
        .update(is_available=False)
    
    return HttpResponseRedirect("/restaurant/menus")
    
@require_POST
def toggle_takeaway(request: HttpRequest):
    req_allow_takeaway = "box" in request.POST

    Restaurant.objects.update(allow_takeaway=req_allow_takeaway)
    
    return HttpResponseRedirect("/restaurant/menus")

@require_POST
def toggle_restaurant(request: HttpRequest):
    req_is_opened = "is_opened" in request.POST

    Restaurant.objects.update(is_opened=req_is_opened)
    
    return HttpResponseRedirect("/restaurant/menus")

@require_GET
def statistics_page(request: HttpRequest):
    return render(request, "restaurant/statistics.html")