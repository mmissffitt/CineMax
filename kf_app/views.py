from django.shortcuts import render, get_object_or_404, redirect
from .models import MediaContent, ContentParticipation, Season, Episode

def index(request):
    movies_sample = MediaContent.objects.filter(content_type='MOVIE')[:4] 
    series_sample = MediaContent.objects.filter(content_type='SERIES')[:4] 
    
    # Получаем имя пользователя из сессии
    username = request.session.get('username', None)
    
    context = {
        'movies_sample': movies_sample,
        'series_sample': series_sample,
        'title': 'Главная страница CINEMAX',
        'username': username,
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

# Страница входа
def login_view(request):
    if request.method == 'POST':
        # Простая "аутентификация" - просто запоминаем в сессии
        username = request.POST.get('username')
        if username:
            request.session['is_authenticated'] = True
            request.session['username'] = username
            return redirect('kf_app:index')
    
    context = {
        'title': 'Вход в CINEMAX'
    }
    return render(request, 'kf_app/login.html', context)

# Страница регистрации
def register_view(request):
    if request.method == 'POST':
        # Простая "регистрация" - просто запоминаем в сессии
        username = request.POST.get('username')
        email = request.POST.get('email')
        if username:
            request.session['is_authenticated'] = True
            request.session['username'] = username
            request.session['email'] = email
            return redirect('kf_app:index')
    
    context = {
        'title': 'Регистрация в CINEMAX'
    }
    return render(request, 'kf_app/register.html', context)

# Страница профиля
def profile_view(request):
    if not request.session.get('is_authenticated'):
        return redirect('kf_app:login')
    
    username = request.session.get('username')
    email = request.session.get('email')
    
    context = {
        'title': f'Профиль - {username}',
        'username': username,
        'email': email,
    }
    return render(request, 'kf_app/profile.html', context)

# Выход
def logout_view(request):
    # Очищаем сессию
    request.session.flush()
    return redirect('kf_app:index')