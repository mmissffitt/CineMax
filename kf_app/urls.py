from django.urls import path
from . import views

app_name = 'kf_app' # Пространство имен приложения

urlpatterns = [
    path('', views.index, name='index'),
    path('movies/', views.movies_list, name='movies_list'),
    path('series/', views.series_list, name='series_list'),
    # path('movie/<int:pk>/', views.movie_detail, name='movie_detail'),
    # path('series/<int:pk>/', views.series_detail, name='series_detail'), #это для будущего
]