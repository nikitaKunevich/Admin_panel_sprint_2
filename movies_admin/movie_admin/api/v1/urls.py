from django.urls import path

from movie_admin.api.v1 import views

urlpatterns = [
    path('movies/', views.MoviesListApi.as_view()),
    path('movies/<str:id>', views.MovieDetailApi.as_view())
]
