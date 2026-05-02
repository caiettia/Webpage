from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Case, When, Value, IntegerField
from urllib.parse import urlencode
from .models import Project, Tag

def portfolio(request):
    prioritized_titles = [
        'TideEye',
        'Dude Wheres My Board',
        'My Personal Site',
        'WMATA DC Metro Analysis',
        'Hype Words',
        'NOAA Waves and Buoys',
        'Visualizing Bird Migrations',
        'Regularization Techniques',
    ]
    portfolio_order = Case(
        *[
            When(title=title, then=Value(index))
            for index, title in enumerate(prioritized_titles)
        ],
        default=Value(len(prioritized_titles)),
        output_field=IntegerField(),
    )
    projects = Project.objects.prefetch_related('tags').annotate(
        portfolio_order=portfolio_order
    ).order_by('portfolio_order', 'id')
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
