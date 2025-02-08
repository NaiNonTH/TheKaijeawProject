from django.shortcuts import render

# Create your views here.
def loginpage(request):
    return render(request,"loginpage.html")

def orderpage(request):
    return render(request,"orderpage.html")

def summarypage(request):
    return render(request,"summarypage.html")

def fillingtogglepage(request):
    return render(request,"fillingtogglepage.html")