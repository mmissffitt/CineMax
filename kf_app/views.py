from django.shortcuts import render
from .models import MediaContent


def index(request):
    movies_sample = MediaContent.objects.filter(content_type='MOVIE')[:4] 
    series_sample = MediaContent.objects.filter(content_type='SERIES')[:4] 
    context = {
        'movies_sample': movies_sample,
        'series_sample': series_sample,
        'title': 'Главная страница CINEMAX',
    }
    return render(request, 'kf_app/index.html', context)

def movies_list(request):
    movies = MediaContent.objects.filter(content_type='MOVIE').order_by('-release_date')
    context = {
        'movies': movies,
    }
    return render(request, 'kf_app/movies.html', context)

def series_list(request):
    series = MediaContent.objects.filter(content_type='SERIES').order_by('-release_date')
    context = {
        'series': series,
    }
    return render(request, 'kf_app/series.html', context)