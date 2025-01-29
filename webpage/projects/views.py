from django.shortcuts import render, get_object_or_404
from .models import Project, Tag

def portfolio(request):
    projects = Project.objects.all()
    tags = Tag.objects.all()
    return render(request, 'portfolio.html', {'projects': projects, 'tags': tags})

def projects_by_tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    projects = tag.projects.all()
    tags = Tag.objects.all()
    return render(request, 'portfolio.html', {'projects': projects, 'tags': tags, 'selected_tag': tag})

def home(request):
    return render(request, 'home.html')

def experience(request):
    return render(request, 'experience.html')