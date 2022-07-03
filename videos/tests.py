from django.test import TestCase
from django.utils.text import slugify
from djangoflix.db.models import PublishStateOptions
from .models import Video
from django.utils import timezone
# Create your tests here.


class VideoModelTestCase(TestCase):
    def setUp(self):
        self.obj_a = Video.objects.create(title='this is my title', video_id='abs')
        self.obj_b = Video.objects.create(title='this is my title', state=PublishStateOptions.PUBLISH, video_id='asdasd')

    def test_slug_field(self):
        title = self.obj_a.title
        test_slug = slugify(title)
        self.assertEqual(test_slug, self.obj_a.slug)

    def test_valid_title(self):
        title = 'this is my title'
        qs = Video.objects.filter(title=title)
        self.assertTrue(qs.exists())

    def test_created_count(self):
        qs = Video.objects.all()
        self.assertEqual(qs.count(), 2)

    def test_draft_case(self):
        obj = Video.objects.filter(state=PublishStateOptions.DRAFT).first()
        self.assertFalse(obj.is_published)

    def test_publish_case(self):
        obj = Video.objects.filter(state=PublishStateOptions.PUBLISH).first()
        self.assertTrue(obj.is_published)

    def test_publish_manager(self):
        published_qs = Video.objects.all().published()
        published_qs_2 = Video.objects.published()
        self.assertTrue(published_qs.exists())
        self.assertEqual(published_qs.count(), published_qs_2.count())
