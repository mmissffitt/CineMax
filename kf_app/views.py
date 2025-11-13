from django.shortcuts import render, get_object_or_404
from .models import MediaContent, ContentParticipation, Season, Episode

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

def movie_detail(request, pk):
    movie = get_object_or_404(MediaContent, pk=pk, content_type='MOVIE')
    participants = ContentParticipation.objects.filter(media_content=movie).select_related('person')
    
    context = {
        'media': movie,
        'participants': participants,
    }
    return render(request, 'kf_app/movie_detail.html', context)

def series_detail(request, pk):
    series = get_object_or_404(MediaContent, pk=pk, content_type='SERIES')
    participants = ContentParticipation.objects.filter(media_content=series).select_related('person')
    seasons = series.season_set.all().prefetch_related('episode_set')
    
    total_episodes = 0
    for season in seasons:
        total_episodes += season.episode_set.count()
    
    context = {
        'media': series,
        'participants': participants,
        'seasons': seasons,
        'total_episodes': total_episodes,
    }
    return render(request, 'kf_app/series_detail.html', context)

def episode_detail(request, episode_id):
    episode = get_object_or_404(Episode, pk=episode_id)
    season = episode.season
    series = season.media_content
    
    context = {
        'episode': episode,
        'season': season,
        'series': series,
    }
    return render(request, 'kf_app/episode_detail.html', context)