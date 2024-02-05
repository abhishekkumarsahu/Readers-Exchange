from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Data(models.Model):
    username = models.CharField(max_length=255)
    fname = models.CharField(max_length=255)
    lname = models.CharField(max_length=255)
    phone = models.IntegerField()
    email = models.EmailField()

    def __str__(self):
        return self.username

class Books(models.Model):
    title = models.CharField(max_length=255)
    username = models.ForeignKey(Data, on_delete=models.CASCADE)
    author = models.CharField(max_length=255)
    publication_date = models.DateField()
    ISBN = models.CharField(max_length=13)
    genre = models.CharField(max_length=100)
    language = models.CharField(max_length=50)
    summary = models.TextField()
    # price = models.DecimalField(max_digits=10, decimal_places=2)
    # is_available = models.BooleanField(default=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
