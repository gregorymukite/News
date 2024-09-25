from django.db import models

# Create your models here.
class News(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    pub_date = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=100, null=True, blank=True)
    author = models.CharField(max_length=100, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    image = models.URLField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title

