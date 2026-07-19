from django.http import HttpResponse

def home(request):
    return HttpResponse("Hello from Tornado!")

# Create your views here.

def index(request):
    return HttpResponse("Hello from the weather app!")

from django.shortcuts import render
from .models import Tornado

def tornado_list(request):
    tornadoes = Tornado.objects.all()

    ef_filter = request.GET.get("ef")
    if ef_filter:
        tornadoes = tornadoes.filter(ef_rating=ef_filter)

    sort = request.GET.get("sort", "-date")
    tornadoes = tornadoes.order_by(sort)

    return render(request, "weather/tornado_list.html", {
        "tornadoes": tornadoes,
        "ef_choices": Tornado.EF_CHOICES if hasattr(Tornado, "EF_CHOICES") else None,
    })