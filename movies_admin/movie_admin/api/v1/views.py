import logging
from contextlib import suppress
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage
from django.db.models import QuerySet
from django.http import JsonResponse, Http404
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movie_admin.models import FilmWork
from utils import model_to_dict_extended

logger = logging.getLogger(__name__)


@dataclass
class MovieResult:
    id: UUID
    title: str
    description: Optional[str]
    creation_date: Optional[datetime]
    rating: Optional[float]
    type: Optional[str]
    genres: Optional[List[str]]
    actors: Optional[List[str]]
    directors: Optional[List[str]]
    writers: Optional[List[str]]

    @classmethod
    def from_filmwork(cls, filmwork):
        genres = [genre.name for genre in filmwork.genres.all()]
        logger.debug(genres)
        actors = []
        directors = []
        writers = []
        person_roles = filmwork.personfilmwork_set.select_related('person').all()
        for person_role in person_roles:
            if person_role.role == 'actor':
                actors.append(person_role.person.full_name)
            if person_role.role == 'director':
                directors.append(person_role.person.full_name)
            if person_role.role == 'writer':
                writers.append(person_role.person.full_name)
        logging.debug(f"{filmwork=}")
        film_work_data = model_to_dict_extended(filmwork, ('id', 'title', 'description', 'creation_date', 'rating', 'type'))
        return cls(**film_work_data, genres=genres, actors=actors, directors=directors, writers=writers)


@dataclass
class MovieListResult:
    count: int
    total_pages: int
    prev: Optional[int]
    next: Optional[int]
    results: List[MovieResult]


class MoviesApiMixin:
    model = FilmWork

    def render_to_response(self, context):
        return JsonResponse(context, json_dumps_params={'ensure_ascii': False})


class MoviesListApi(MoviesApiMixin, BaseListView):
    http_method_names = ['get']
    ordering = ['title']
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        logger.error('get_context_data')

        paginator = context['paginator']
        page = context['page_obj']
        # noinspection PyUnusedLocal
        prev_page = next_page = None

        with suppress(EmptyPage):
            prev_page = page.previous_page_number()
        with suppress(EmptyPage):
            next_page = page.next_page_number()

        film_works: QuerySet = context['object_list']
        logger.debug(f'film_works: {len(film_works)} {film_works}')
        film_works = film_works.prefetch_related('genres', 'personfilmwork_set', 'persons')

        result_movies = []
        for filmwork in film_works:
            result_movies.append(MovieResult.from_filmwork(filmwork))

        return asdict(MovieListResult(count=paginator.count,
                                      total_pages=paginator.num_pages,
                                      prev=prev_page,
                                      next=next_page,
                                      results=result_movies))


class MovieDetailApi(MoviesApiMixin, BaseDetailView):
    http_method_names = ['get']

    pk_url_kwarg = 'id'

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except ValidationError:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        filmwork = context['object']

        return asdict(MovieResult.from_filmwork(filmwork))
