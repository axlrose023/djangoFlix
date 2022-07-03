from django.contrib import admin
from .models import Image, ImageAllProxy, ImagePublishedProxy
from djangoflix.db.models import PublishStateOptions

# Register your models here.


class ImageAllProxyAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'state', 'image_id', 'is_published')
    search_fields = ('title',)
    list_filter = ('state', 'active')
    readonly_fields = ('id', 'is_published', 'publish_timestamp')

    class Meta:
        model = ImageAllProxy


admin.site.register(ImageAllProxy, ImageAllProxyAdmin)


class ImagePublishedProxyAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'state', 'image_id', 'is_published')
    search_fields = ['title']
    list_filter = ('state', 'active')
    readonly_fields = ('id', 'is_published', 'publish_timestamp')

    class Meta:
        model = ImagePublishedProxy

    def get_queryset(self, request):
        return ImagePublishedProxy.objects.filter(active=True, state=PublishStateOptions.PUBLISH)


admin.site.register(ImagePublishedProxy, ImagePublishedProxyAdmin)
