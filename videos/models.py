from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.db.models.signals import pre_save
# Create your models here.
from djangoflix.db.models import PublishStateOptions
from djangoflix.db.receivers import publish_state_pre_save, slugify_pre_save


class VideoQuerySet(models.QuerySet):
    def published(self):
        now = timezone.now()
        return self.filter(state=PublishStateOptions.PUBLISH,
                           publish_timestamp__lte=now)


class VideoManager(models.Manager):
    def get_queryset(self):
        return VideoQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()


class Video(models.Model):
    VideoStateOptions = PublishStateOptions
    title = models.CharField(max_length=220)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    # 'this-is-my-video'
    video_id = models.CharField(max_length=220)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    state = models.CharField(max_length=2, choices=PublishStateOptions.choices, default=PublishStateOptions.DRAFT)
    publish_timestamp = models.DateTimeField(auto_now_add=False, auto_now=False, blank=True, null=True)

    objects = VideoManager()

    def get_video_id(self):
        if not self.is_published:
            return None
        return self.video_id

    @property
    def is_published(self):
        if self.active is True and self.state == PublishStateOptions.PUBLISH:
            return True
        else:
            return False

    def get_playlists_ids(self):
        # self.<foreigned_obj>_set.all()
        return list(self.playlist_featured.all().values_list('id', flat=True))

    def __str__(self):
        return self.title


class VideoAllProxy(Video):
    class Meta:
        proxy = True
        verbose_name = 'All Video'
        verbose_name_plural = 'All Videos'


class VideoPublishedProxy(Video):
    class Meta:
        proxy = True
        verbose_name = 'Published Video'
        verbose_name_plural = 'Published Videos'


pre_save.connect(publish_state_pre_save, sender=Video)

pre_save.connect(slugify_pre_save, sender=Video)
