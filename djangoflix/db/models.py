from django.db import models

# Create your models here.


class PublishStateOptions(models.TextChoices):
    # CONSTANT = DB_VALUE, USER_DISPLAY_VALUE
    PUBLISH = 'PU', 'Publish'
    DRAFT = 'DR', 'DRAFT'
    # UNLISTED = 'UN', 'Unlisted'
    # PRIVATE = 'PR', 'Private'
