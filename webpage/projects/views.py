from django.shortcuts import render
from .models import Project

def portfolio(request):
    projects = Project.objects.all()
    return render(request, 'portfolio.html', {'projects': projects})

def home(request):
    return render(request, 'home.html')