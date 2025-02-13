from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from .models import Filling, Egg, Order

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
            egg_amount = Egg.objects.get(pk=request.POST['egg'])

            if len(Order.objects.all()) == 0:
                queue_number = 1
                print(queue_number)
            else:
                recent_order = Order.objects.latest("date")
                max_queue_number = 24
                queue_number = recent_order.queue_number % max_queue_number + 1

            new_order = Order.objects.create(
                queue_number=queue_number,
                egg_amount=egg_amount
            )
            new_order.save()

            fillings_list = request.POST.getlist("filling")

            for filling_name in fillings_list:
                filling = Filling.objects.get(pk=filling_name)
                new_order.fillings.add(filling)
        except:
            context = {
                "status_code": 400,
                "message": "Bad Request"
            }

            return render(request, "error.html", context, status=400)
        
        context = {
            "queue_number": queue_number,
            "price": egg_amount.price
        }

        return render(request, "queuepage.html", context)
    else:
        context = {
            "status_code": 405,
            "message": "Method not Allowed"
        }

        return render(request, "error.html", context, status=405)