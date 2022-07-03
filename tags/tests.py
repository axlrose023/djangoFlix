from django.test import TestCase
from django.db.utils import IntegrityError
from .models import TaggedItem
from playlists.models import Playlist
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

class TaggedItemTestCase(TestCase):
    def setUp(self):
        ply_title = 'New Title'
        self.ply_obj = Playlist.objects.create(title=ply_title)
        self.ply_title = ply_title
        self.ply_obj.tags.add(TaggedItem(tag='New tag'), bulk=False)
        # self.tag_a = TaggedItem.objects.create(tag='My-new-tag')

    def test_content_type_is_not_null(self):
        with self.assertRaises(IntegrityError):
            TaggedItem.objects.create(tag='My-new-tag')

    def test_create_via_content_type(self):
        c_type = ContentType.objects.get(app_label='playlists', model='playlist')
        tag_a = TaggedItem.objects.create(content_type=c_type, object_id=1, tag='new_tag')
        self.assertIsNotNone(tag_a.pk)

    def test_create_via_model_content_type(self):
        c_type = ContentType.objects.get_for_model(Playlist)
        tag_a = TaggedItem.objects.create(content_type=c_type, object_id=2, tag='My tag via model')
        self.assertIsNotNone(tag_a.pk)

    def test_create_via_app_loader_content_type(self):
        PlaylistKlass = apps.get_model(app_label='playlists', model_name='Playlist')
        c_type = ContentType.objects.get_for_model(PlaylistKlass)
        tag_a = TaggedItem.objects.create(content_type=c_type, object_id=3, tag='My tag via app loader')
        self.assertIsNotNone(tag_a.pk)

    def test_related_field(self):
        self.assertEqual(self.ply_obj.tags.count(), 1)

    def test_related_field_create(self):
        self.ply_obj.tags.create(tag="Another Tag")
        self.assertEqual(self.ply_obj.tags.count(), 2)

    def test_related_field_query_name(self):
        qs = TaggedItem.objects.filter(playlist__title__iexact=self.ply_title)
        self.assertEqual(qs.count(), 1)


    def test_related_field_via_content_type(self):
        c_type = ContentType.objects.get_for_model(Playlist)
        tag_qs = TaggedItem.objects.filter(content_type=c_type, object_id=self.ply_obj.id)
        self.assertEqual(tag_qs.count(), 1)

