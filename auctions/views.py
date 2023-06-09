from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .forms import CreateListingForm, BidForm, CommentsForm
from .models import User, Listing, Comments
from django.contrib import messages



def index(request):
    listings = Listing.objects.filter(active=True)

    return render(request, "auctions/index.html",{
        "listings" : listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)

            # Redirect user
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    messages.warning(request, 'You are now logged out.')
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required()
def new_listing(request):

    if request.method == "POST":
        form = CreateListingForm(request.POST)

        if form.is_valid():
            form.instance.user = request.user
            added_listing = form.save()
            messages.success(request, "Listing Created")
            return HttpResponseRedirect(reverse("listing", args=[added_listing.pk]))

    return render(request, "auctions/newlisting.html", {
        "form": CreateListingForm()
        })


def listing(request, listing_id):

    listing = Listing.objects.get(pk=listing_id)

    return render(request, "auctions/listing.html", {
        "id" : listing.id,
        "title": listing.title,
        "description": listing.description,
        "image_url": listing.image,
        "created": listing.user,
        "price": listing.highest_bid(),
        "bidform": BidForm(),
        "bid_count": listing.bidcount(),
        "watch_list": listing.watchlist_exist(request.user),
        "addcomments": CommentsForm(),
        "comments": listing.comments.all(),
        "commentscount": listing.comments.all().count()
    })


@login_required
def bid(request, listing_id):

    if request.method == "POST":
        form = BidForm(request.POST)

        if form.is_valid():
            bid_amount = form.cleaned_data['amount']
            listing = Listing.objects.get(pk=listing_id)

            if listing.highest_bid() >= bid_amount:
                messages.error(request, 'Please ensure your bid exceeds the current highest bid.')
            else:
                form.instance.user = request.user
                form.instance.listing = listing
                form.save()
                messages.success(request, "Your bid has been successfully added.")
                HttpResponseRedirect(reverse("listing", args=[listing_id]))

    return HttpResponseRedirect(reverse('listing', args=[listing_id]))


@login_required
def watchlistchange(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        user = request.user

        if listing.watchlist_exist(user):
            listing.watchlist.remove(user)
            messages.warning(request, "Item removed from watchlist.")
            return HttpResponseRedirect(reverse('listing', args=[listing_id]))
        else:
            listing.watchlist.add(user)
            messages.success(request, "Item successfully added to watchlist.")
            return HttpResponseRedirect(reverse('listing', args=[listing_id]))


@login_required
def watchlist(request):
    
    return render(request, "auctions/watchlist.html", {
        "watchlist": request.user.watch_list.all()
    })


@login_required
def unwatch(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        user = request.user

        if listing.watchlist_exist(user):
            listing.watchlist.remove(user)
            messages.error(request, "Item removed from watchlist.")
            return HttpResponseRedirect(reverse("watchlist"))
        else:
            messages.error(request, "Item is not in watchlist")


@login_required
def comment(request, listing_id):
    
    if request.method == "POST":
        
        form = CommentsForm(request.POST)

        if form.is_valid():
            form.instance.user = request.user
            form.instance.listing = Listing.objects.get(pk=listing_id)
            form.save()
            messages.success(request, "Comment added successfully.")
            return HttpResponseRedirect(reverse('listing', args=[listing_id]))
        else:
            messages.error(request, "Failed to add comment. Please try again later.")
            return HttpResponseRedirect(reverse('listing', args=[listing_id]))
    


