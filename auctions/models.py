from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return self.category


class Listing(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.URLField(null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default="", blank=True, null=True, related_name="listings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")

    def __str__(self):
        return f"{self.title} by {self.user}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)