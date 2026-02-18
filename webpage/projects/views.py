from django.shortcuts import render, redirect, get_object_or_404
from urllib.parse import urlencode
from .models import Project, Tag

def portfolio(request):
    projects = Project.objects.prefetch_related('tags').all()
    tags = Tag.objects.all()
    selected_tag = request.GET.get('tag', '').strip()
    return render(request, 'portfolio.html', {
        'projects': projects,
        'tags': tags,
        'selected_tag': selected_tag,
    })

def projects_by_tag(request, tag_name):
    get_object_or_404(Tag, name=tag_name)
    query = urlencode({'tag': tag_name})
    return redirect('portfolio' + '?' + query, permanent=False)

def home(request):
    return render(request, 'home.html')

def experience(request):
    return render(request, 'experience.html')