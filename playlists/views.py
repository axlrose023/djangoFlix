from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q, Max
from django.shortcuts import render
from .models import MovieProxy, TVShowProxy, Playlist, TVShowSeasonProxy
from django.views.generic import ListView, DetailView
from django.http import Http404
from django.utils import timezone
from djangoflix.db.models import PublishStateOptions
from .mixins import PlaylistMixin


# Create your views here.


class SearchView(PlaylistMixin, ListView):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        query = self.request.GET.get('q')
        if query is not None:
            context['title'] = f"Searched for {query}"
        else:
            context['title'] = f"Perform a search for {query}"
        return context

    def get_queryset(self, query=None):
        query = self.request.GET.get('q')

        return Playlist.objects.all().movie_or_show().search(query=query)


class MovieListView(PlaylistMixin, ListView):
    queryset = MovieProxy.objects.all()
    title = 'Movies'
    paginate_by = 6
    # context_object_name = 'movies'


class TVShowListView(PlaylistMixin, ListView):
    queryset = TVShowProxy.objects.all().published()
    title = 'TV Shows'
    # context_object_name = 'tvshow'


class FeaturedPlaylistListView(ListView):
    template_name = 'playlists/featured_list.html'
    queryset = Playlist.objects.featured_playlists().published()
    title = 'Актуальні Плейлісти'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.title is not None:
            context['title'] = self.title
        context['shows'] = TVShowProxy.objects.all()
        context['movies'] = MovieProxy.objects.all()
        context['movies_rate'] = MovieProxy.objects.all().filter(ratings__value__in='5')
        context['shows_rate'] = TVShowProxy.objects.all().filter(ratings__value__in='5')
        return context

    def get_queryset(self):
        return super().get_queryset().published()


class MovieDetailView(PlaylistMixin, DetailView):
    template_name = 'playlists/movie_detail.html'
    queryset = MovieProxy.objects.all()


class PlaylistDetailView(PlaylistMixin, DetailView):
    template_name = 'playlists/playlist_detail.html'
    queryset = Playlist.objects.all()


class TVShowSeasonDetailView(DetailView):
    template_name = 'playlists/tvshow_season_detail.html'
    queryset = TVShowSeasonProxy.objects.all()

    # context_object_name = 'season'

    def get_object(self, queryset=None):
        show_slug = self.kwargs.get('showSlug')
        season_slug = self.kwargs.get('seasonSlug')
        now = timezone.now()
        try:
            obj = TVShowSeasonProxy.objects.get(
                state=PublishStateOptions.PUBLISH,
                parent__slug__iexact=show_slug,
                slug__iexact=season_slug,
                publish_timestamp__lte=now
            )
        except TVShowSeasonProxy.MultipleObjectsReturned:
            obj = TVShowSeasonProxy.objects.filter(
                parent__slug__iexact=show_slug,
                slug__iexact=season_slug,
                publish_timestamp__lte=now
            ).published()
        except:
            raise Http404
        return obj


class TVShowDetailView(PlaylistMixin, DetailView):
    template_name = 'playlists/tvshow_detail.html'
    queryset = TVShowProxy.objects.all()



