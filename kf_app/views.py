from django.shortcuts import render, get_object_or_404, redirect
from .models import MediaContent, ContentParticipation, Season, Episode

REGISTERED_USERS = {}

def index(request):
    # Обработка формы обратной связи
    if request.method == 'POST' and 'name' in request.POST:
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        request.session['feedback_success'] = True
        return redirect('kf_app:index')
    
    # Берем флаг из сессии и СРАЗУ УДАЛЯЕМ его
    feedback_success = request.session.pop('feedback_success', False)
    
    movies_sample = MediaContent.objects.filter(content_type='MOVIE')[:4] 
    series_sample = MediaContent.objects.filter(content_type='SERIES')[:4] 
    
    username = request.session.get('username', None)
    
    context = {
        'movies_sample': movies_sample,
        'series_sample': series_sample,
        'title': 'Главная страница CINEMAX',
        'username': username,
        'feedback_success': feedback_success,
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
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Проверяем существование пользователя в глобальном словаре
        if username in REGISTERED_USERS and REGISTERED_USERS[username]['password'] == password:
            request.session['is_authenticated'] = True
            request.session['username'] = username
            request.session['email'] = REGISTERED_USERS[username]['email']
            return redirect('kf_app:index')
        else:
            context = {
                'title': 'Вход в CINEMAX',
                'error': 'Неверное имя пользователя или пароль'
            }
            return render(request, 'kf_app/login.html', context)
    
    context = {
        'title': 'Вход в CINEMAX'
    }
    return render(request, 'kf_app/login.html', context)

# Страница регистрации
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            context = {
                'title': 'Регистрация в CINEMAX',
                'error': 'Пароли не совпадают'
            }
            return render(request, 'kf_app/register.html', context)
        
        # Сохраняем пользователя в глобальный словарь
        REGISTERED_USERS[username] = {
            'email': email,
            'password': password
        }
        
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
    request.session.flush()
    return redirect('kf_app:index')
