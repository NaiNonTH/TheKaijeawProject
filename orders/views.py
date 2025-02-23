from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponseRedirect

from django.views.decorators.http import require_GET, require_POST
from django.db.models import Q
from django.db.models.aggregates import Sum, Count
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test

from .models import Filling, Egg, Order, Restaurant, Validator
from .utils import OrderBuilder

from datetime import date

# Create your views here.

def user_check(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return user.groups.filter(name='Staff').exists()

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/restaurant/orders')
        else:
            return render(request, 'login.html', {
                'error': 'Invalid username or password.'
            })
    else:
        return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

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
    
@user_passes_test(user_check, login_url='/login')
def restaurant_menu_page(request: HttpRequest):
    fillings = list(Filling.objects.all())
    restaurant = Restaurant.objects.last()

    context = {
        "fillings": fillings,
        "restaurant": restaurant
    }

    return render(request, "restaurant/menupage.html", context)

@user_passes_test(user_check, login_url='/login')
def orders_page(request: HttpRequest):
    orders = list(Order.objects.filter(is_completed=False).all())

    context = {
        "orders": orders
    }

    return render(request, "restaurant/orderspage.html", context)

@user_passes_test(user_check, login_url='/login')
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

@user_passes_test(user_check, login_url='/login')
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

@user_passes_test(user_check, login_url='/login')    
@require_POST
def toggle_takeaway(request: HttpRequest):
    req_allow_takeaway = "box" in request.POST

    Restaurant.objects.update(allow_takeaway=req_allow_takeaway)
    
    return HttpResponseRedirect("/restaurant/menus")

@user_passes_test(user_check, login_url='/login')
@require_POST
def toggle_restaurant(request: HttpRequest):
    req_is_opened = "is_opened" in request.POST

    Restaurant.objects.update(is_opened=req_is_opened)
    
    return HttpResponseRedirect("/restaurant/menus")

@user_passes_test(user_check, login_url='/login')
@require_GET
def statistics_page(request: HttpRequest):
    filtered = request.method == "GET" and "date" in request.GET

    if filtered:
        year, month, day = request.GET["date"].split("-")
        filter_date = date(int(year), int(month), int(day))
    else:
        filter_date = date.today()

    selected_orders = Order.objects.filter(date__date=filter_date)

    order_count = selected_orders.count()
    
    counts = selected_orders.aggregate(
        egg_count=Sum("egg_amount__amount", default=0),
        grossing=Sum("egg_amount__price", default=0)
    )
    
    fillings_title = [filling.title for filling in Filling.objects.all()]
    fillings_count = []
    
    for title in fillings_title:
        fillings_count.append(
            selected_orders.aggregate(title=Count("fillings__name", filter=Q(fillings__title=title)))["title"]
        )

    order_times = list(range(0, 24))
    order_count_at_time = []

    for hour in order_times:
        order_count_at_time.append(
            selected_orders.filter(date__hour=hour).count()
        )

    context = {
        "order_count": order_count,
        "egg_count": counts["egg_count"],
        "grossing": counts["grossing"],
        "filter_date": str(filter_date),
        "fillings_graph": {
            "x": fillings_title,
            "y": fillings_count
        },
        "order_time_graph": {
            "x": order_times,
            "y": order_count_at_time
        }
    }

    return render(request, "restaurant/statistics.html", context)