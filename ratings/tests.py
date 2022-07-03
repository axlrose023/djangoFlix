import random
from .models import Rating, RatingChoices
from django.test import TestCase
from django.contrib.auth import get_user_model
from playlists.models import Playlist

# Create your tests here.

User = get_user_model()  # User.objects.all()


class RatingTestCase(TestCase):

    def create_playlists(self):
        playlists = []
        self.playlist_count = random.randint(10, 500)
        for i in range(0, self.playlist_count):
            playlists.append(Playlist(title=f'Playlist_{i}'))
        Playlist.objects.bulk_create(playlists)
        self.playlists = Playlist.objects.all()

    def create_users(self):
        items = []
        self.user_count = random.randint(10, 500)
        for i in range(0, self.user_count):
            items.append(User(username=f'user_{i}'))
        User.objects.bulk_create(items)
        self.users = User.objects.all()

    def create_ratings(self):
        ratings = []
        self.ratings_count = random.randint(10, 500)
        for i in range(0, self.ratings_count):
            user_obj = self.users.order_by('?').first()
            ply_obj = self.playlists.order_by('?').first()
            ratings.append(Rating(
                user=user_obj,
                content_object=ply_obj,
                value=random.choice(RatingChoices.choices)[0]
            ))
        Rating.objects.bulk_create(ratings)
        self.ratings = Rating.objects.all()

    def setUp(self):
        self.create_users()
        self.create_playlists()
        self.create_ratings()

    def test_user_count(self):
        qs = User.objects.all()
        self.assertTrue(qs.exists())
        self.assertEqual(qs.count(), self.user_count)

    def test_playlist_count(self):
        qs = Playlist.objects.all()
        self.assertTrue(qs.exists())
        self.assertEqual(qs.count(), self.playlist_count)

    def test_rating_count(self):
        rating = Rating.objects.all()
        self.assertTrue(rating.exists())
        self.assertEqual(rating.count(), self.ratings_count)

    def test_rating_random_choices(self):
        value_set = set(Rating.objects.values_list('value', flat=True))
        self.assertTrue(len(value_set) > 1)
