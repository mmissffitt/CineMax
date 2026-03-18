from django.urls import path
from . import views

app_name = 'kf_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('movies/', views.movies_list, name='movies_list'),
    path('series/', views.series_list, name='series_list'),
    path('movie/<int:pk>/', views.movie_detail, name='movie_detail'),
    path('series/<int:pk>/', views.series_detail, name='series_detail'),
    path('episode/<int:episode_id>/', views.episode_detail, name='episode_detail'),
    
    path('api/filter-content/', views.filter_content_api, name='filter_content_api'),
    path('api/search/', views.search_api, name='search_api'),  
    
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
]