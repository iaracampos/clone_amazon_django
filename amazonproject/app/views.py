from django.shortcuts import render
from .models import *

# Create your views here.
def index(request):
    products = Produto.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'app/index.html', context)