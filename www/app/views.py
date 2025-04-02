from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponseRedirect

from django.views.decorators.http import require_GET, require_POST

from django.db.models import Q
from django.db.models.aggregates import Sum, Count

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import user_passes_test

from .models import Filling, Egg, Order, Restaurant
from .utils import OrderBuilder, send_order_changes

from . import forms

from datetime import date
import json

# Create your views here.

@require_GET
def menu_page(request: HttpRequest):
    restaurant = Restaurant.objects.last()

    # ถ้าร้านปิด หรือ admin ยังไม่ได้เพิ่มข้อมูลร้านค้า
    if restaurant is None or not restaurant.is_opened:
        return render(request, "customer/closed.html")

    # เลือกไส้ จำนวนไข่ และกล่อง(จากร้าน) ที่เก็บไว้ใน database มาใช้แสดงเมนู

    fillings = Filling.objects.all()
    eggs = Egg.objects.all()

    context = {
        "fillings": fillings,
        "eggs": eggs,
        "restaurant": restaurant
    }

    response = render(request, "customer/menupage.html", context)

    # เมื่อถูก redirect กลับมาจาก save_order() เพราะ input ไม่ผ่าน
    # ให้แสดงข้อความ error จาก cookie ที่เก็บไว้จาก save_order()
    if request.COOKIES.get("success", "True") == "False" and request.COOKIES.get("error_type", "") == "INVALID_REQUEST":
        context["error_message"] = json.loads(request.COOKIES.get("error_message"))
        
        response = render(request, "customer/menupage.html", context)

        response.delete_cookie("error_message")
        response.delete_cookie("success")

    return response

@require_POST
def save_order(request: HttpRequest):
    if not Restaurant.objects.last().is_opened:
        return HttpResponseRedirect("/")
    
    fillings_list = request.POST.getlist("filling")
    is_takeaway = "is_takeaway" in request.POST

    # ใช้ try..except ดักกรณีที่คิวเต็ม
    try:
        # ตรวจสอบข้อมูลแล้วสร้าง builder object เมื่อ input ถูกต้อง
        # รวมทั้งกำหนดจำนวนไข่ให้ object
        # แต่สร้างเฉพาะ dict ของข้อความ error เมื่อไม่ถูกต้อง
        order_builder, error_message = OrderBuilder.validate_and_create(request.POST)
    
        # ถ้า input ไม่ถูกต้อง ให้ redirect กลับไปหน้าเมนูพร้อมแสดงข้อความ error
        if order_builder is None:
            response = HttpResponseRedirect("/")
    
            # ใช้ cookie เก็บข้อมูลของ error สำหรับแสดงในหน้า view ถัดไป
            response.set_cookie("success", "False")
            response.set_cookie("error_type", "INVALID_REQUEST")
            response.set_cookie("error_message", json.dumps(error_message)) # ต้อง serialize ข้อมูล ใช้ json.dumps()
    
            return response

        new_order = order_builder                   \
                    .add_fillings(fillings_list)    \
                    .takeaway(is_takeaway)          \
                    .build()
        
        new_order.save()
        
        response = HttpResponseRedirect("queue")

        # คำสั่งซื้อใหม่ถูกเก็บเข้า database สำเร็จ
        # เก็บหมายเลขคิวกับราคาไว้สำหรับหน้า queue
        response.set_cookie("success", "True")
        response.set_cookie("queue_number", new_order.queue_number)
        response.set_cookie("price", new_order.egg_amount.price)

        send_order_changes(new_order)

    except OrderBuilder.NoQueueLeftError:
        response = HttpResponseRedirect("queue")
        response.set_cookie("success", "False")
        response.set_cookie("error_type", "NO_QUEUE_LEFT")
    
    return response

@require_GET
def queue_page(request: HttpRequest):
    # ถ้าลูกค้าเข้ามาโดยที่ยังไม่ได้สั่ง ให้ redirect ไปที่หน้าเมนู
    if "success" not in request.COOKIES:
        return HttpResponseRedirect("/")
    
    # คำสั่งซื้อสำเร็จ (คิวไม่เต็ม)
    if request.COOKIES.get("success", "True") == "True":
        context = {
            "queue_number": request.COOKIES.get('queue_number'),
            "price": request.COOKIES.get('price')
        }

        # ไม่ลบคุกกี้ เผื่อลูกค้าอยาก refresh หน้า queue เลขจะได้ไม่หายจนกว่าจะสั่งใหม่

        return render(request, "customer/queuepage.html", context)
    else:
        if request.COOKIES.get('error_type') == "NO_QUEUE_LEFT":
            message = "ไม่มีคิวว่าง"
        else:
            message = "เกิดข้อผิดพลาด"

        context = {
            "message": message
        }

        response = render(request, "customer/error.html", context)

        response.delete_cookie("success")
        response.delete_cookie("error_type")

        return response

def restaurant_section(request):
    return HttpResponseRedirect("/restaurant/orders")

# ตรวจสอบการยืนยันตัวตนของผู้ใช้
def user_check(user):
    # ยังไม่ล็อกอิน
    if not user.is_authenticated:
        return False
    # เป็น admin หรือ staff (ร้านค้า)
    if user.is_superuser or user.is_staff:
        return True
    # อยู่ในกลุ่ม Staff
    return user.groups.filter(name='Staff').exists()

def login_view(request: HttpRequest):
    # ถ้าล็อกอินแล้ว ให้ข้ามการยืนยันตัวตน
    if request.user.is_authenticated:
        return HttpResponseRedirect("/restaurant/orders")
    
    # ถ้าเคยล็อกอินแล้วไม่ผ่าน ให้ view แสดงข้อความ error ผ่าน context นี้
    context = {
        "error": request.COOKIES.get("login_error") == "True" # เป็น boolean True ถ้าล็อกอินไม่สำเร็จ
    }

    response = render(request, 'restaurant/login.html', context)
    response.delete_cookie("login_error")

    return response

@require_POST
def restaurant_authentication(request: HttpRequest):
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(request, username=username, password=password)

    # ถ้ามีชื่อ user ในระบบและ password ถูกต้อง ให้ล็อกอินผู้ใช้นั้นแล้วให้เข้าสู่ระบบได้
    if user is not None:
        login(request, user)
        
        return redirect('/restaurant/orders')
    else:
        # ถ้า request มาจากหน้าล็อกอิน
        if request.resolver_match.view_name == "login":
            redirect_url = request.get_full_path()
        else:
            # ใช้ default
            redirect_url = "/restaurant/login"

        # ให้ผู้ใช้กลับไปล็อกอินใหม่
        response = HttpResponseRedirect(redirect_url)
        response.set_cookie("login_error", "True")

        return response

@require_POST
def logout_view(request):
    logout(request)
    return redirect('login')
    
@user_passes_test(user_check, login_url='/restaurant/login/')
def restaurant_menu_page(request: HttpRequest):
    fillings = list(Filling.objects.all())
    restaurant = Restaurant.objects.last()

    context = {
        "fillings": fillings,
        "restaurant": restaurant
    }

    return render(request, "restaurant/menupage.html", context)

@user_passes_test(user_check, login_url='/restaurant/login/')
def orders_page(request: HttpRequest):
    orders = list(Order.objects.filter(is_completed=False).all())

    context = {
        "orders": orders,
        "status_updated": request.COOKIES.get("status_updated")
    }
    
    response = render(request, "restaurant/orderspage.html", context)
    response.delete_cookie("status_updated")

    return response

@user_passes_test(user_check, login_url='/restaurant/login/')
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

@user_passes_test(user_check, login_url='/restaurant/login/')
@require_POST
def update_status(request: HttpRequest):
    req_fillings =  request.POST.getlist("filling")
    req_allow_takeaway = "box" in request.POST
    req_is_opened = "is_opened" in request.POST

    Filling.objects                     \
        .filter(name__in=req_fillings)  \
        .update(is_available=True)
    
    Filling.objects                     \
        .exclude(name__in=req_fillings) \
        .update(is_available=False)
    
    Restaurant.objects.update(allow_takeaway=req_allow_takeaway)

    Restaurant.objects.update(is_opened=req_is_opened)

    response = HttpResponseRedirect("/restaurant/orders")
    response.set_cookie("status_updated", True)

    return response

@user_passes_test(user_check, login_url='/restaurant/login/')
@require_GET
def statistics_page(request: HttpRequest):
    filtered = request.method == "GET" and "date" in request.GET

    invalid_date = False

    if filtered:
        year, month, day = request.GET["date"].split("-")

        try:
            filter_date = date(int(year), int(month), int(day))
        except:
            invalid_date = True
            filter_date = date.today()
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
        "invalid_date": invalid_date,
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

@user_passes_test(user_check, login_url='/restaurant/login/')
def more_page(request: HttpRequest):
    response = render(request, "restaurant/morepage.html", {
        "status": request.COOKIES.get("status", 0)
    })
    response.delete_cookie("status")

    return response

@user_passes_test(user_check, login_url='/restaurant/login/')
def restaurant_config(request: HttpRequest):
    restaurant = Restaurant.objects.last()
    form = forms.RestaurantForm(instance=restaurant)

    response = render(request, "restaurant/restaurant.html", {
        "form": form,
        "status": request.COOKIES.get("status", 0)
    })
    response.delete_cookie("status")

    return response

@user_passes_test(user_check, login_url='/restaurant/login/')
@require_POST
def change_restaurant_info(request: HttpRequest):
    restaurant = Restaurant.objects.last()
    form = forms.RestaurantForm(request.POST)
    

    if form.is_valid():
        restaurant.queue_capacity = request.POST["queue_capacity"]
        restaurant.max_fillings = request.POST["max_fillings"]
        restaurant.save()
        
        response = redirect("/restaurant/more")
        response.set_cookie("status", 1)
    else:
        response = redirect("/restaurant/restaurant")
        response.set_cookie("status", -1)

    return response

@user_passes_test(user_check, login_url='/restaurant/login/')
def password_config(request: HttpRequest):
    context = {
        "status": request.COOKIES.get("status", 0)
    }

    response = render(request, "restaurant/password.html", context)
    response.delete_cookie("status")

    return response

@user_passes_test(user_check, login_url='/restaurant/login/')
@require_POST
def password_change(request:HttpRequest):
    current_password = request.POST['current-password']

    response = redirect("/restaurant/password")

    if request.user.check_password(current_password):
        new_password_one = request.POST['new-password']
        new_password_two = request.POST['new-password-confirm']

        if (new_password_one == new_password_two):
            request.user.set_password(new_password_one)
            request.user.save()
            update_session_auth_hash(request, request.user)

            response = redirect("/restaurant/more")
            response.set_cookie("status", 1)
        else:
            response.set_cookie("status", -1)

    else:
        response.set_cookie("status", -2)

    return response