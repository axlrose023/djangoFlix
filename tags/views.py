from django.http import Http404
from django.shortcuts import render
from django.views.generic import ListView
from django.views import View
# Create your views here.
from playlists.mixins import PlaylistMixin
from playlists.models import Playlist
from tags.models import *
from django.views.generic import ListView, DetailView


class TaggedItemListView(View):
    def get(self, request):
        tag_list = TaggedItem.objects.unique_list()
        context = {
            'tag_list': tag_list
        }
        return render(request, 'tags/tags_list.html', context)


class TaggedItemDetailView(ListView, PlaylistMixin):
    template_name = 'playlist_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        context['title'] = f"{self.kwargs.get('tag')}".title()
        return context

    def get_queryset(self):
        tag = self.kwargs.get('tag')
        return Playlist.objects.filter(tags__tag=tag).movie_or_show()
