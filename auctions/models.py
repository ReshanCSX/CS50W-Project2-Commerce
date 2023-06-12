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
    watchlist = models.ManyToManyField(User, blank=True, related_name="watchlist")

    def __str__(self):
        return f"{self.title} by {self.user}"
    
    def bidcount(self):
        return self.bids.all().count()
    
    def highest_bid(self):
        if self.bidcount() is 0:
            return self.starting_bid
        else:
            return round(self.bids.aggregate(price = models.Max('amount'))['price'],2) #https://docs.djangoproject.com/en/4.2/topics/db/aggregation/

    def watchlist_exist(self, user):
        return self.watchlist.filter(pk=user.id).exists() # https://stackoverflow.com/questions/8461819/checking-for-objects-existence-in-manytomany-relation-django


    def user_in_bids(self, user):
        return self.bids.filter(user=user.id).exists()

    def highest_bid_user(self):
        if self.bidcount() is 0:
            return None
        else:
            return self.bids.get(amount=self.highest_bid()).user

        


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.amount} by {self.user.id}"
    

class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=1000)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.comment} by {self.user} in {self.listing}"