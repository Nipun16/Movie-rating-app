from django.urls import path

from . import views

urlpatterns = [
    path('api/scrap_movies', views.scrap_movies),
    path('api/get_movies', views.MovieListView.as_view()),
    path('api/get_movie_by_id/<int:movie_id>', views.get_movie_by_id),
    path('api/get_to_watch_movies', views.get_to_watch_movies),
    path('api/get_watched_movies', views.get_watched_movies),
    path('api/add_movie', views.add_movie),
    path('api/delete_movie', views.delete_movie)
]
