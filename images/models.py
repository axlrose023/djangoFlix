from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_save

from djangoflix.db.models import PublishStateOptions


# Create your models here.


class ImageQuerySet(models.QuerySet):
    def published(self):
        now = timezone.now()
        return self.filter(state=PublishStateOptions.PUBLISH,
                           publish_timestamp__lte=now)


class ImageManager(models.Manager):
    def get_queryset(self):
        return ImageQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()


class Image(models.Model):
    ImageStateOptions = PublishStateOptions
    title = models.CharField(max_length=50)
    url = models.URLField()
    image_id = models.IntegerField()
    active = models.BooleanField(default=True)
    publish_timestamp = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)
    state = models.CharField(max_length=2, choices=PublishStateOptions.choices,
                             default=PublishStateOptions.DRAFT)

    objects = ImageManager()

    def __str__(self):
        return self.title

    def is_published(self):
        if self.active is True and self.state == PublishStateOptions.PUBLISH:
            return True
        else:
            return False

    def get_img_id(self):
        if not self.is_published():
            return None
        return self.image_id


class ImageAllProxy(Image):
    class Meta:
        proxy = True
        verbose_name = 'All Image'
        verbose_name_plural = 'All Images'


class ImagePublishedProxy(Image):
    class Meta:
        proxy = True
        verbose_name = 'Published Image'
        verbose_name_plural = 'Published Images'


def publish_state_pre_save(sender, instance, *args, **kwargs):
    is_published = instance.state = PublishStateOptions.PUBLISH
    is_draft = instance.state = PublishStateOptions.DRAFT
    if is_published and instance.publish_timestamp is None:
        instance.publish_timestamp = timezone.now()
    elif is_draft:
        instance.publish_timestamp = None


pre_save.connect(publish_state_pre_save, sender=Image)

