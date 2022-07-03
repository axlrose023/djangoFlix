from django.db.models.signals import post_save
from .models import CustomUser, Profile
from django.dispatch import receiver


@receiver(post_save, sender=CustomUser)
def build_profile(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        Profile.objects.create(user=user)


@receiver(post_save, sender=CustomUser)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
