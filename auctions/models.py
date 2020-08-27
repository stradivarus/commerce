from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ModelForm


class User(AbstractUser):
    watchlist = models.ManyToManyField("Listing")
    # watchlist = models.CharField(max_length=300, default="")


class Listing(models.Model):
    TOYS = 'toys'
    PHONES = 'phones'
    STRAWBERRY = 'strawberry'
    MANGO = 'mango'
    CATEGORY_CHOICES = [
        (TOYS, 'Toys'),
        (PHONES, 'Phones'),
        (STRAWBERRY, 'Strawberry'),
        (MANGO, 'Mango')
    ]

    title = models.CharField(max_length=120)
    description = models.TextField()
    start_bid = models.FloatField()
    image = models.URLField(blank=True)
    category = models.CharField(max_length=20, blank=True, choices=CATEGORY_CHOICES)
    date = models.DateField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid = models.FloatField()


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'start_bid', 'image', 'category']

