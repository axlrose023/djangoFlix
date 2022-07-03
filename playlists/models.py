from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Avg, Max, Min, Q
from images.models import Image
from tags.models import TaggedItem
from django.utils import timezone
from django.utils.text import slugify
from django.db.models.signals import pre_save
# Create your models here.
from djangoflix.db.models import PublishStateOptions
from djangoflix.db.receivers import publish_state_pre_save, slugify_pre_save, \
    unique_slugify_pre_save
from videos.models import Video
from categories.models import Category
from ratings.models import Rating


class PlaylistQuerySet(models.QuerySet):
    def published(self):
        now = timezone.now()
        return self.filter(state=PublishStateOptions.PUBLISH,
                           publish_timestamp__lte=now)

    def movie_or_show(self):
        return self.filter(
            Q(type=Playlist.PlaylistTypeChoices.MOVIE) |
            Q(type=Playlist.PlaylistTypeChoices.SHOW)
        )

    def search(self, query=None):
        if query is None:
            return self
        return self.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__title__icontains=query) |
            Q(category__slug__icontains=query) |
            Q(tags__tag__icontains=query)
        ).distinct()


class PlaylistManager(models.Manager):
    def get_queryset(self):
        return PlaylistQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()

    def featured_playlists(self):
        return self.get_queryset().filter(type=Playlist.PlaylistTypeChoices.PLAYLIST)


class Playlist(models.Model):
    class PlaylistTypeChoices(models.TextChoices):
        MOVIE = "MOV", "Movie"
        SHOW = 'TVS', "TV Show"
        SEASON = "SEA", "SEASON"
        PLAYLIST = "PL", "PLAYLIST"

    image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.SET_NULL)
    related = models.ManyToManyField('self', blank=True, related_name='related',
                                     through='PlaylistRelated')
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL,
                                 related_name='playlists')

    order = models.IntegerField(default=1)
    title = models.CharField(max_length=220)
    type = models.CharField(max_length=3, choices=PlaylistTypeChoices.choices, default=PlaylistTypeChoices.PLAYLIST)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    # Foreign key // one video per playlist
    video = models.ForeignKey(Video, blank=True, null=True, on_delete=models.SET_NULL, related_name='playlist_featured')
    videos = models.ManyToManyField(Video, blank=True, through='PlaylistItem', related_name='playlist_item')
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    state = models.CharField(max_length=2, choices=PublishStateOptions.choices, default=PublishStateOptions.DRAFT)
    publish_timestamp = models.DateTimeField(auto_now_add=False, auto_now=False, blank=True, null=True)
    tags = GenericRelation(TaggedItem, related_query_name='playlist')
    ratings = GenericRelation(Rating, related_query_name='playlist')

    objects = PlaylistManager()

    def get_related_items(self):
        return self.playlistrelated_set.all()

    def get_absolute_url(self):
        if self.is_movie:
            return f"/movies/{self.slug}/"
        if self.is_show:
            return f"/shows/{self.slug}"
        if self.is_season and self.parent is not None:
            return f"/shows/{self.parent.slug}/seasons/{self.slug}/"
        return f"/playlists/{self.slug}"

    @property
    def is_movie(self):
        return self.type == self.PlaylistTypeChoices.MOVIE

    @property
    def is_season(self):
        return self.type == self.PlaylistTypeChoices.SEASON

    @property
    def is_show(self):
        return self.type == self.PlaylistTypeChoices.SHOW

    @property
    def is_published(self):
        return self.active

    def __str__(self):
        return self.title

    def get_rating_avg(self):
        return Playlist.objects.filter(id=self.id).aggregate(Avg('rating__value'))

    def get_rating_spread(self):
        return Playlist.objects.filter(id=self.id).aggregate(Max('rating__value'))

    def get_short_display(self):
        return

    def get_video_id(self):
        if self.video is None:
            return None
        return self.video.get_video_id()

    def get_clips(self):
        return self.playlistitem_set.all().published()


class TVShowProxyManager(PlaylistManager):
    def all(self):
        return self.get_queryset().filter(parent__isnull=True, type=Playlist.PlaylistTypeChoices.SHOW)


class MovieProxyManager(PlaylistManager):
    def all(self):
        return self.get_queryset().filter(type=Playlist.PlaylistTypeChoices.MOVIE)


class MovieProxy(Playlist):
    objects = MovieProxyManager()

    def get_movie_id(self):
        # get movie id to render movie for users
        return self.video.get_video_id()

    def get_clips(self):
        # get clips to render clips for users
        return self.playlistitem_set.all().published()

    class Meta:
        proxy = True
        verbose_name = 'Movie'
        verbose_name_plural = "Movies"

    def save(self, *args, **kwargs):
        self.type = Playlist.PlaylistTypeChoices.MOVIE
        super().save(*args, **kwargs)


class TVShowProxy(Playlist):
    objects = TVShowProxyManager()

    class Meta:
        verbose_name = 'TV Show'
        verbose_name_plural = "TV Shows"
        proxy = True

    def save(self, *args, **kwargs):
        self.type = Playlist.PlaylistTypeChoices.SHOW
        super().save(*args, **kwargs)

    @property
    def seasons(self):
        return self.playlist_set.published()

    def get_short_display(self):
        return f"{self.seasons.count()} Seasons"

    def get_video_id(self):
        if self.video is None:
            return None
        return self.video.get_video_id()

    def get_clips(self):
        return self.playlistitem_set.all().published()


class TVShowSeasonManager(PlaylistManager):

    def all(self):
        return self.get_queryset().filter(parent__isnull=False, type=Playlist.PlaylistTypeChoices.SEASON)


class TVShowSeasonProxy(Playlist):
    objects = TVShowSeasonManager()

    class Meta:
        verbose_name = 'Season'
        verbose_name_plural = "Seasons"
        proxy = True

    def save(self, *args, **kwargs):
        self.type = Playlist.PlaylistTypeChoices.SEASON
        super().save(*args, **kwargs)

    def get_episodes(self):
        return self.playlistitem_set.all()

    def get_season_trailer(self):
        return self.get_video_id()


class PlaylistItemQuerySet(models.QuerySet):
    def published(self):
        now = timezone.now()
        return self.filter(playlist__state=PublishStateOptions.PUBLISH,
                           playlist__publish_timestamp__lte=now,
                           video__state=PublishStateOptions.PUBLISH,
                           video__publish_timestamp__lte=now)


class PlaylistItemManager(models.Manager):
    def get_queryset(self):
        return PlaylistItemQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()


class PlaylistItem(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = PlaylistItemManager()

    # qs = PlaylistItem.objects.filter(playlist=playlist_obj).order_by('order')

    class Meta:
        ordering = ['order', '-timestamp']


def pr_limit_choices_to():
    return Q(type=Playlist.PlaylistTypeChoices.MOVIE) | Q(type=Playlist.PlaylistTypeChoices.SHOW)
    # qs = Playlist.objects.filter(type=Playlist.PlaylistTypeChoices.MOVIE)
    # qs2 = Playlist.objects.filter(type=Playlist.PlaylistTypeChoices.SHOW)
    # final_qs = qs | qs2


class PlaylistRelated(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    related = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='related_item',
                                limit_choices_to=pr_limit_choices_to)
    order = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)


pre_save.connect(publish_state_pre_save, sender=TVShowProxy)
pre_save.connect(unique_slugify_pre_save, sender=TVShowProxy)

pre_save.connect(publish_state_pre_save, sender=MovieProxy)
pre_save.connect(unique_slugify_pre_save, sender=MovieProxy)

pre_save.connect(publish_state_pre_save, sender=TVShowSeasonProxy)
pre_save.connect(unique_slugify_pre_save, sender=TVShowSeasonProxy)

pre_save.connect(publish_state_pre_save, sender=Playlist)
pre_save.connect(unique_slugify_pre_save, sender=Playlist)
