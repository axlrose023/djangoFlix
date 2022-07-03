from django.test import TestCase
from django.utils import timezone

from playlists.models import TVShowProxy, TVShowSeasonProxy
from videos.models import Video, PublishStateOptions


class TestTVShowProxyModel(TestCase):
    def create_videos(self):
        self.title = 'My videos'
        self.video_a = Video.objects.create(title=self.title, video_id='123adsav11')
        self.video_b = Video.objects.create(title=self.title, video_id='12e44t511',
                                            state=PublishStateOptions.PUBLISH)
        self.video_qs = Video.objects.all()

    def setUp(self):
        self.create_videos()
        self.tv_show_a = TVShowProxy.objects.create(title=self.title, video=self.video_a)
        self.tv_show_b = TVShowProxy.objects.create(title=self.title, video=self.video_b,
                                                    state=PublishStateOptions.PUBLISH)

    def test_tv_show_title(self):
        title = self.title
        qs = TVShowProxy.objects.filter(title=title)
        self.assertEqual(qs.count(), 2)

    def test_tv_show_video_exists(self):
        qs = TVShowProxy.objects.filter(video=self.video_a)
        self.assertTrue(qs.exists())

    def test_tv_show_state_draft(self):
        qs = TVShowProxy.objects.filter(state=PublishStateOptions.DRAFT)
        self.assertEqual(qs.count(), 1)

    def test_tv_show_state_publish(self):
        now = timezone.now()
        qs = TVShowProxy.objects.filter(state=PublishStateOptions.PUBLISH, publish_timestamp__lte=now)
        self.assertEqual(qs.count(), 1)

    def test_created_count(self):
        qs = TVShowProxy.objects.all().count()
        self.assertEqual(qs, 2)

    # def test_show_has_seasons(self):
    #     seasons = self.tv_show_a.playlist_set.all()
    #     self.assertTrue(seasons.exists()) Need to create seasons at setUp

