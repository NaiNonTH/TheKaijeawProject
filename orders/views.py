from django.shortcuts import render
from django.http import HttpResponse

from .models import Filling, Egg

# Create your views here.

def menupage(request):
    fillings = Filling.objects.all()
    eggs = Egg.objects.all()

    context = {
        "fillings": fillings,
        "eggs": eggs
    }

    return render(request, "menupage.html", context)

def queuepage(request):
    return render(request, "queuepage.html")