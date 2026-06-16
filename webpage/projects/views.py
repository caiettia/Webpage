from django.shortcuts import render, redirect
from urllib.parse import urlencode


STATIC_PORTFOLIO_URL = "https://acaietti.com/portfolio/"


def _portfolio_redirect_url(tag_name: str | None = None) -> str:
    if not tag_name:
        return STATIC_PORTFOLIO_URL
    query = urlencode({"tag": tag_name})
    return f"{STATIC_PORTFOLIO_URL}?{query}"

def portfolio(request):
    return redirect(_portfolio_redirect_url(), permanent=False)

def projects_by_tag(request, tag_name):
    return redirect(_portfolio_redirect_url(tag_name.strip()), permanent=False)

def home(request):
    return render(request, 'home.html')

def experience(request):
    return render(request, 'experience.html')
