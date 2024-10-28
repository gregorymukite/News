from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class News(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='news_items')
    title = models.CharField(max_length=200)
    description = models.TextField( null= True)
    pub_date = models.DateTimeField(null=True, blank=True)  # Consider auto_now_add=True if you want automatic date
    source = models.CharField(max_length=100, null=True, blank=True)
    author = models.CharField(max_length=100, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    image = models.URLField(null=True, blank=True)  # Could be ImageField for file uploads
    content = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title
