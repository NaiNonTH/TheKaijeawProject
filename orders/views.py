from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from .models import Filling, Egg, Order, NoQueueLeftError, NoEggAmountSpecifiedError, TooManyFillingsError

# Create your views here.

def menupage(request: HttpRequest):
    fillings = Filling.objects.all()
    eggs = Egg.objects.all()

    context = {
        "fillings": fillings,
        "eggs": eggs
    }

    return render(request, "menupage.html", context)

def queuepage(request: HttpRequest):
    if request and request.method == "POST":
        try:
            if "egg" not in request.POST:
                raise NoEggAmountSpecifiedError

            fillings_list = request.POST.getlist("filling")

            if len(fillings_list) > 3:
                raise TooManyFillingsError

            egg_amount = Egg.objects.get(pk=request.POST['egg'])

            if len(Order.objects.filter(is_completed=False).all()) == 0:
                queue_number = 1
            else:
                incompleted_orders = Order.objects.filter(is_completed=False)
                unavailable_queues = [order.queue_number for order in list(incompleted_orders.all())]

                max_queue_number = 24

                if len(unavailable_queues) == max_queue_number:
                    raise NoQueueLeftError

                queue_number = unavailable_queues[-1] % max_queue_number + 1

                while queue_number in unavailable_queues:
                    queue_number = (queue_number + 1) % max_queue_number

            new_order = Order.objects.create(
                queue_number=queue_number,
                egg_amount=egg_amount
            )
            new_order.save()

            for filling_name in fillings_list:
                filling = Filling.objects.get(pk=filling_name)
                new_order.fillings.add(filling)

        except NoQueueLeftError:
            context = {
                "is_error": False,
                "status_code": 400,
                "message": "ไม่มีคิวว่าง"
            }

            return render(request, "error.html", context, status=400)
        except NoEggAmountSpecifiedError:
            context = {
                "is_error": False,
                "status_code": 400,
                "message": "ท่านไม่ได้ระบุจำนวนไข่"
            }
            
            return render(request, "error.html", context, status=400)
        except TooManyFillingsError:
            context = {
                "is_error": False,
                "status_code": 400,
                "message": "ท่านเลือกไส้เกิน 3 ตัวเลือก"
            }

            return render(request, "error.html", context, status=400)
        except Exception:
            context = {
                "is_error": True,
                "status_code": 500,
                "message": "เกิดข้อผิดพลาดโดยไม่ทราบสาเหตุในระบบ"
            }

            return render(request, "error.html", context, status=500)
        
        context = {
            "queue_number": queue_number,
            "price": egg_amount.price
        }

        return render(request, "queuepage.html", context)
    else:
        context = {
            "is_error": False,
            "status_code": 405,
            "message": "ท่านไม่ได้เข้ามาหน้านี้อย่างถูกต้อง"
        }

        return render(request, "error.html", context, status=405)