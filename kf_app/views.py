from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import MediaContent, ContentParticipation, Season, Episode, Genre

REGISTERED_USERS = {}

def index(request):
    if request.method == 'POST' and 'name' in request.POST:
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        request.session['feedback_success'] = True
        return redirect('kf_app:index')
    
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
    genres = Genre.objects.all()

    items_per_page = min(12, movies.count()) if movies.count() > 0 else 12
    if items_per_page == 0:
        items_per_page = 12
    
    paginator = Paginator(movies, items_per_page)
    page = request.GET.get('page', 1)
    movies_page = paginator.get_page(page)
    
    context = {
        'movies': movies_page,
        'genres': genres,
        'total_pages': paginator.num_pages,
    }
    return render(request, 'kf_app/movies.html', context)

def series_list(request):
    series = MediaContent.objects.filter(content_type='SERIES').order_by('-release_date')
    genres = Genre.objects.all()
    
    items_per_page = min(12, series.count()) if series.count() > 0 else 12
    if items_per_page == 0:
        items_per_page = 12
    
    paginator = Paginator(series, items_per_page)
    page = request.GET.get('page', 1)
    series_page = paginator.get_page(page)
    
    context = {
        'series': series_page,
        'genres': genres,
        'total_pages': paginator.num_pages,
    }
    return render(request, 'kf_app/series.html', context)

def filter_content_api(request):
    """API endpoint для фильтрации контента"""
    content_type = request.GET.get('type', 'movie')
    page = int(request.GET.get('page', 1))
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '-release_date')
    genre_ids = request.GET.getlist('genres[]')
    
    # Определяем тип контента
    if content_type == 'movie':
        db_content_type = 'MOVIE'
        template_name = 'kf_app/includes/movie_card.html'
        context_var = 'movie'
    else:
        db_content_type = 'SERIES'
        template_name = 'kf_app/includes/series_card.html'
        context_var = 'serie'
    
    # Базовый запрос
    queryset = MediaContent.objects.filter(content_type=db_content_type)
    
    # Поиск
    if search:
        queryset = queryset.filter(title__icontains=search)
    
    # Фильтр по жанрам
    if genre_ids:
        queryset = queryset.filter(genres__id__in=genre_ids).distinct()
    
    # Сортировка
    queryset = queryset.order_by(sort)
    
    # Пагинация
    paginator = Paginator(queryset, 12)
    current_page = paginator.get_page(page)
    
    # Формируем HTML для карточек
    from django.template.loader import render_to_string
    
    html = ''
    for item in current_page:
        html += render_to_string(template_name, {context_var: item})
    
    return JsonResponse({
        'html': html,
        'has_next': current_page.has_next(),
        'total_pages': paginator.num_pages,
        'current_page': page,
    })

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

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
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

def logout_view(request):
    request.session.flush()
    return redirect('kf_app:index')

def search_api(request):
    """API для поиска в хедере"""
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    movies = MediaContent.objects.filter(
        content_type='MOVIE',
        title__icontains=query
    )[:5]
    
    series = MediaContent.objects.filter(
        content_type='SERIES',
        title__icontains=query
    )[:5]
    
    results = []
    
    for movie in movies:
        results.append({
            'id': movie.id,
            'title': movie.title,
            'type': 'movie',
            'poster': movie.poster.url if movie.poster else None,
            'year': movie.release_date.year if movie.release_date else 'N/A',
            'rating': movie.rating,
        })
    
    for serie in series:
        results.append({
            'id': serie.id,
            'title': serie.title,
            'type': 'series',
            'poster': serie.poster.url if serie.poster else None,
            'year': serie.release_date.year if serie.release_date else 'N/A',
            'rating': serie.rating,
        })
    
    return JsonResponse({'results': results})