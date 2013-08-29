from django.db import models


GENERIC = 0
ADMIN = 1
ACTIVITY = 2
TAG_CATEGORIES = ((GENERIC, "Generic"),
                  (ADMIN, "Admin"),
                  (ACTIVITY, "Activity"),)


class Tag(models.Model):
    name = models.CharField(max_length=150,)
    description = models.TextField(null=True, blank=True)
    category = models.IntegerField("Tag Category", choices=TAG_CATEGORIES,)

    def __unicode__(self):
        return self.name
